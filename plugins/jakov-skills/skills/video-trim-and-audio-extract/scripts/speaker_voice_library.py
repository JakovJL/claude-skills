#!/usr/bin/env python3
"""Local speaker-voice library: enroll confident voice samples per person, then
identify the anonymous speakers of a new diarized transcript against it.

Context comes first. The cheapest way to name "Speaker 1/2/3" is still who was
invited and what they say (people address each other by name). This tool is the
fallback for when context is not enough: it compares each speaker's voice with
samples of people already identified in earlier recordings.

Everything runs locally. Audio is decoded with ffmpeg, embeddings come from a
speaker-verification ONNX model through sherpa-onnx, and nothing is uploaded.
Voice embeddings are biometric personal data: the library lives in a local
folder (default ~/.config/voice_library, override with --library or
VOICE_LIBRARY_DIR), never in a repository, and should only hold people who
agreed to it.

Input is the word-level JSON that `video_tail_trim.py transcribe --save-json`
writes (ElevenLabs Scribe: words with start/end/speaker_id). Speaker ids are
numbered by first appearance, matching the "Speaker N" labels of the .txt.

Subcommands:
    map-labels  propose speaker_id -> person from a hand-labeled transcript of
                the same recording ("email:" lines or "[Speaker N] - email")
    enroll      cut confident single-speaker stretches for the given
                speaker_id=person pairs and add them to the library
    identify    score each speaker of a new recording against the library
    list        show who is enrolled and how much audio backs each person
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

SAMPLE_RATE = 16000
DEFAULT_LIBRARY = Path(os.environ.get("VOICE_LIBRARY_DIR", Path.home() / ".config" / "voice_library"))
# NVIDIA TitaNet-Large, exported for sherpa-onnx. Codec and capture conditions
# can affect scores; thresholds are heuristics, not identity guarantees.
DEFAULT_MODEL = "nemo_en_titanet_large.onnx"
MODEL_URL = ("https://github.com/k2-fsa/sherpa-onnx/releases/download/"
             "speaker-recongition-models/" + DEFAULT_MODEL)

# A stretch is "confident" only when the diarizer had no reason to doubt it:
# long enough to carry a stable voiceprint, clear of neighbouring turns so a
# boundary error cannot leak the other speaker in, and free of audio events.
MIN_SEG_S = 4.0
MAX_SEG_S = 12.0
GUARD_S = 0.4
PAUSE_SPLIT_S = 1.5


# ---------------------------------------------------------------- transcript

def load_turns(json_path: Path) -> list[dict]:
    """Group words into speaker turns, splitting a turn on long pauses."""
    words = json.loads(json_path.read_text(encoding="utf-8"))["words"]
    turns: list[dict] = []
    for w in words:
        kind = w.get("type")
        if kind == "spacing":
            continue
        spk = w.get("speaker_id") or "speaker_?"
        cur = turns[-1] if turns else None
        new_turn = (cur is None or cur["speaker"] != spk
                    or w["start"] - cur["end"] > PAUSE_SPLIT_S)
        if new_turn:
            cur = {"speaker": spk, "start": w["start"], "end": w["end"],
                   "words": [], "events": 0}
            turns.append(cur)
        cur["end"] = max(cur["end"], w["end"])
        if kind == "audio_event":
            cur["events"] += 1
        else:
            cur["words"].append(w["text"])
    for t in turns:
        t["text"] = " ".join(t["words"])
    return turns


def speaker_order(turns: list[dict]) -> list[str]:
    seen: list[str] = []
    for t in turns:
        if t["speaker"] not in seen:
            seen.append(t["speaker"])
    return seen


def confident_segments(turns: list[dict], speaker: str) -> list[tuple[float, float]]:
    """Clean stretches of one speaker, cut into MAX_SEG_S windows."""
    out: list[tuple[float, float]] = []
    for i, t in enumerate(turns):
        if t["speaker"] != speaker or t["events"] or len(t["words"]) < 8:
            continue
        start, end = t["start"] + GUARD_S, t["end"] - GUARD_S
        if i > 0 and turns[i - 1]["end"] > t["start"] - GUARD_S:
            continue  # previous speaker still talking: possible overlap
        if i + 1 < len(turns) and turns[i + 1]["start"] < t["end"] + GUARD_S:
            continue
        while end - start >= MIN_SEG_S:
            chunk_end = min(start + MAX_SEG_S, end)
            if chunk_end - start >= MIN_SEG_S:
                out.append((round(start, 2), round(chunk_end, 2)))
            start = chunk_end
    return out


# ------------------------------------------------------------ labeled text

LABEL_EMAIL = re.compile(r"^([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+):\s*$")
LABEL_BRACKET = re.compile(r"^\[(Speaker \d+)\](?:\s*-\s*(\S+@\S+?))?\s*$")
LABEL_NAMED = re.compile(r"^([^:\[\]]{2,60}):\s+(.*)$")


def load_labeled(path: Path) -> list[tuple[str, str]]:
    """(person, text) turns from a hand-labeled transcript, any of three shapes."""
    declared: dict[str, str] = {}
    turns: list[tuple[str, str]] = []
    who: str | None = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        m = LABEL_EMAIL.match(line)
        if m:
            who = m.group(1)
            continue
        m = LABEL_BRACKET.match(line)
        if m:
            if m.group(2):
                declared[m.group(1)] = m.group(2)
            who = declared.get(m.group(1), m.group(1))
            continue
        m = LABEL_NAMED.match(line)
        if m and not line.startswith("http"):
            turns.append((m.group(1).strip(), m.group(2)))
            who = m.group(1).strip()
            continue
        if who:
            turns.append((who, line))
    return turns


TOKEN = re.compile(r"\w{3,}", re.UNICODE)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in TOKEN.findall(text)}


def map_labels(turns: list[dict], labeled: list[tuple[str, str]]) -> dict[str, dict]:
    """Vote speaker_id -> person by matching turn text, weighted by words.

    Two transcriptions of one recording word turns differently, so matching is
    by token overlap within a sliding window around the same relative position.
    """
    lab_tokens = [(p, _tokens(t)) for p, t in labeled]
    votes: dict[str, Counter] = defaultdict(Counter)
    n_lab = max(len(lab_tokens), 1)
    for i, t in enumerate(turns):
        toks = _tokens(t["text"])
        if len(toks) < 4:
            continue
        centre = int(i / max(len(turns), 1) * n_lab)
        best, best_score = None, 0.0
        for j in range(max(0, centre - 40), min(n_lab, centre + 40)):
            person, lt = lab_tokens[j]
            if not lt:
                continue
            score = len(toks & lt) / len(toks | lt)
            if score > best_score:
                best, best_score = person, score
        if best and best_score >= 0.3:
            votes[t["speaker"]][best] += len(t["words"])
    result = {}
    for spk, c in votes.items():
        person, weight = c.most_common(1)[0]
        result[spk] = {"person": person, "purity": round(weight / sum(c.values()), 2),
                       "votes": dict(c.most_common(4))}
    return result


# ------------------------------------------------------------------- audio

def load_audio(path: Path):
    import numpy as np
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "f32le", "-"],
        # stdin closed: ffmpeg otherwise reads the caller's stdin and, inside a
        # shell loop over a file list, swallows the rest of the list.
        stdin=subprocess.DEVNULL, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


class Embedder:
    def __init__(self, library: Path, model: str | None = None):
        import sherpa_onnx
        model_path = Path(model) if model else library / "models" / DEFAULT_MODEL
        if not model_path.exists():
            raise SystemExit(f"speaker model not found: {model_path}\nDownload it once: {MODEL_URL}")
        cfg = sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=str(model_path), num_threads=4)
        self._ex = sherpa_onnx.SpeakerEmbeddingExtractor(cfg)

    def __call__(self, samples):
        import numpy as np
        stream = self._ex.create_stream()
        stream.accept_waveform(SAMPLE_RATE, samples)
        stream.input_finished()
        v = np.array(self._ex.compute(stream), dtype=np.float32)
        return v / (np.linalg.norm(v) + 1e-9)


def _clip(audio, start: float, end: float):
    return audio[int(start * SAMPLE_RATE):int(end * SAMPLE_RATE)]


def _slug(person: str) -> str:
    return re.sub(r"[^\w.@-]+", "_", person.strip()).strip("_")


# ----------------------------------------------------------------- library

def person_dir(library: Path, person: str) -> Path:
    return library / "people" / _slug(person)


def load_library(library: Path) -> dict[str, "object"]:
    import numpy as np
    people = {}
    root = library / "people"
    if not root.is_dir():
        return people
    for d in sorted(root.iterdir()):
        emb = d / "embeddings.npy"
        meta = d / "person.json"
        if emb.exists() and meta.exists():
            name = json.loads(meta.read_text(encoding="utf-8"))["person"]
            people[name] = np.load(emb)
    return people


def cmd_map_labels(args) -> int:
    turns = load_turns(Path(args.json))
    labeled = load_labeled(Path(args.labeled))
    mapping = map_labels(turns, labeled)
    order = speaker_order(turns)
    for spk in order:
        m = mapping.get(spk)
        n = sum(len(t["words"]) for t in turns if t["speaker"] == spk)
        label = f"Speaker {order.index(spk) + 1}"
        if m:
            flag = "OK " if m["purity"] >= args.min_purity else "LOW"
            print(f"{flag} {spk} ({label}, {n} words) -> {m['person']}  purity={m['purity']}  votes={m['votes']}")
        else:
            print(f"--  {spk} ({label}, {n} words) -> no match")
    return 0


def cmd_enroll(args) -> int:
    import numpy as np
    import soundfile as sf
    library = Path(args.library)
    turns = load_turns(Path(args.json))
    audio = load_audio(Path(args.audio))
    embed = Embedder(library, args.model)
    for pair in args.speaker:
        spk, person = pair.split("=", 1)
        segs = confident_segments(turns, spk)
        segs.sort(key=lambda s: s[1] - s[0], reverse=True)
        segs = sorted(segs[:args.max_segments])
        if not segs:
            print(f"{person}: no confident segments for {spk}, skipped")
            continue
        d = person_dir(library, person)
        (d / "clips").mkdir(parents=True, exist_ok=True)
        (d / "person.json").write_text(json.dumps({"person": person}, ensure_ascii=False), encoding="utf-8")
        manifest = d / "manifest.jsonl"
        known = set()
        if manifest.exists():
            for line in manifest.read_text(encoding="utf-8").splitlines():
                e = json.loads(line)
                known.add((e["source"], e["start"]))
        vectors, added = [], 0
        with manifest.open("a", encoding="utf-8") as mf:
            for start, end in segs:
                if (Path(args.audio).name, start) in known:
                    continue
                clip = _clip(audio, start, end)
                vectors.append(embed(clip))
                clip_name = f"{Path(args.audio).stem}_{start:08.2f}.wav"
                sf.write(d / "clips" / clip_name, clip, SAMPLE_RATE)
                mf.write(json.dumps({"source": Path(args.audio).name, "speaker_id": spk, "start": start,
                                     "end": end, "clip": clip_name,
                                     "added": dt.date.today().isoformat()}, ensure_ascii=False) + "\n")
                added += 1
        if vectors:
            emb_path = d / "embeddings.npy"
            old = np.load(emb_path) if emb_path.exists() else np.zeros((0, len(vectors[0])), dtype=np.float32)
            np.save(emb_path, np.vstack([old, np.array(vectors)]))
        total = sum((e - s) for s, e in segs)
        print(f"{person}: +{added} segment(s) from {spk} ({total:.0f}s of confident audio)")
    return 0


def _centroid(vectors):
    import numpy as np
    c = vectors.mean(axis=0)
    return c / (np.linalg.norm(c) + 1e-9)


def cmd_enroll_pair(args) -> int:
    """Two-person recording, one voice already enrolled: no transcript needed.

    Every window that clearly is the known person is theirs, every window that
    clearly is not is the other participant's, and the unclear middle is
    discarded. The other side is then checked for internal consistency, which
    is what catches a third voice (a joiner, a video playing) that a
    two-person assumption would otherwise enroll under the wrong name.
    """
    import numpy as np
    import soundfile as sf
    library = Path(args.library)
    people = load_library(library)
    if args.known not in people:
        raise SystemExit(f"{args.known} is not enrolled; enroll-pair needs one known voice")
    known_c = _centroid(people[args.known])
    audio = load_audio(Path(args.audio))
    embed = Embedder(library, args.model)
    win, hop = int(args.window * SAMPLE_RATE), int(args.hop * SAMPLE_RATE)
    rms_floor = args.min_rms
    starts, vecs = [], []
    for s in range(0, max(len(audio) - win, 0), hop):
        clip = audio[s:s + win]
        if float(np.sqrt((clip ** 2).mean())) < rms_floor:
            continue  # silence or near-silence carries no voiceprint
        starts.append(s / SAMPLE_RATE)
        vecs.append(embed(clip))
    if not vecs:
        raise SystemExit("no voiced windows found")
    vecs = np.array(vecs)
    to_known = vecs @ known_c
    known_mask = to_known >= args.known_min
    other_mask = to_known <= args.other_max
    n = len(vecs)
    print(f"{n} voiced windows: {known_mask.sum()} {args.known}, {other_mask.sum()} other, "
          f"{n - known_mask.sum() - other_mask.sum()} unclear (discarded)")
    if known_mask.sum() < args.min_windows and not args.one_sided:
        # Without the known voice there is no split to make: the recording may
        # hold only the remote side (fine, but say so with --one-sided), or the
        # known person sounds different on this setup and "not them" would
        # swallow them too.
        print(f"known voice found in only {known_mask.sum()} windows; refusing - pass --one-sided "
              "only if you know this recording captured just the other participant")
        return 1
    if other_mask.sum() < args.min_windows:
        print(f"too few windows for the other participant ({other_mask.sum()} < {args.min_windows}); nothing enrolled")
        return 1
    # Tighten the other side around its own centroid twice, so stray windows
    # of a third voice or of crosstalk fall away before anything is saved.
    idx = np.where(other_mask)[0]
    for _ in range(2):
        c = _centroid(vecs[idx])
        idx = idx[vecs[idx] @ c >= args.cohesion]
    if len(idx) < args.min_windows:
        print(f"other side is not one consistent voice ({len(idx)} coherent windows); nothing enrolled - check by hand")
        return 1
    other_c = _centroid(vecs[idx])
    spread = float(np.mean(vecs[idx] @ other_c))
    rival = sorted(((float(other_c @ _centroid(v)), p) for p, v in people.items() if p != args.other), reverse=True)
    print(f"other voice: {len(idx)} coherent windows, cohesion {spread:.2f}, vs {args.known} {float(other_c @ known_c):.2f}")
    if args.other in people:
        same = float(other_c @ _centroid(people[args.other]))
        print(f"vs existing samples of {args.other}: {same:.2f}")
        if same < 0.65:
            print("existing samples of this person do not match this voice - wrong name or wrong recording; nothing enrolled")
            return 1
    if rival and rival[0][0] >= 0.65:
        print(f"WARNING: other voice already scores {rival[0][0]:.2f} against enrolled {rival[0][1]} - "
              "either the name is wrong or that person is enrolled twice; nothing enrolled")
        return 1
    # Keep the most typical, mutually non-overlapping windows.
    order = sorted(idx, key=lambda i: float(vecs[i] @ other_c), reverse=True)
    chosen: list[int] = []
    for i in order:
        if all(abs(starts[i] - starts[j]) >= args.window for j in chosen):
            chosen.append(i)
        if len(chosen) >= args.max_segments:
            break
    d = person_dir(library, args.other)
    (d / "clips").mkdir(parents=True, exist_ok=True)
    (d / "person.json").write_text(json.dumps({"person": args.other}, ensure_ascii=False), encoding="utf-8")
    source = Path(args.audio).name
    with (d / "manifest.jsonl").open("a", encoding="utf-8") as mf:
        for i in sorted(chosen):
            start, end = round(starts[i], 2), round(starts[i] + args.window, 2)
            clip_name = f"{Path(args.audio).stem}_{start:08.2f}.wav"
            sf.write(d / "clips" / clip_name, _clip(audio, start, end), SAMPLE_RATE)
            mf.write(json.dumps({"source": source, "speaker_id": "pair:other", "start": start, "end": end,
                                 "clip": clip_name, "added": dt.date.today().isoformat()}, ensure_ascii=False) + "\n")
    emb_path = d / "embeddings.npy"
    new = vecs[sorted(chosen)]
    old = np.load(emb_path) if emb_path.exists() else np.zeros((0, new.shape[1]), dtype=np.float32)
    np.save(emb_path, np.vstack([old, new]))
    print(f"{args.other}: +{len(chosen)} segment(s) ({len(chosen) * args.window:.0f}s) from {source}")
    return 0


def _score(emb, person_vectors):
    import numpy as np
    centroid = person_vectors.mean(axis=0)
    centroid /= np.linalg.norm(centroid) + 1e-9
    return float(emb @ centroid)


def cmd_identify(args) -> int:
    import numpy as np
    library = Path(args.library)
    people = load_library(library)
    if args.candidates:
        wanted = {c.strip().lower() for c in args.candidates.split(",") if c.strip()}
        people = {p: v for p, v in people.items() if p.lower() in wanted}
    if not people:
        raise SystemExit("no enrolled people to compare against (check --candidates / the library)")
    turns = load_turns(Path(args.json))
    audio = load_audio(Path(args.audio))
    embed = Embedder(library, args.model)
    report = []
    for idx, spk in enumerate(speaker_order(turns), 1):
        segs = confident_segments(turns, spk)
        segs.sort(key=lambda s: s[1] - s[0], reverse=True)
        segs = segs[:args.max_segments]
        if not segs:
            report.append({"label": f"Speaker {idx}", "speaker_id": spk, "match": None, "reason": "no confident audio"})
            continue
        vecs = np.array([embed(_clip(audio, s, e)) for s, e in segs])
        emb = vecs.mean(axis=0)
        emb /= np.linalg.norm(emb) + 1e-9
        scores = sorted(((round(_score(emb, v), 3), p) for p, v in people.items()), reverse=True)
        best, runner = scores[0], (scores[1] if len(scores) > 1 else (0.0, None))
        margin = round(best[0] - runner[0], 3)
        decided = best[0] >= args.threshold and margin >= args.margin
        report.append({"label": f"Speaker {idx}", "speaker_id": spk, "segments": len(segs),
                       "match": best[1] if decided else None, "score": best[0], "margin": margin,
                       "top": scores[:3]})
    if args.json_out:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for r in report:
            if r.get("match"):
                print(f"{r['label']} ({r['speaker_id']}): {r['match']}  score={r['score']} margin={r['margin']}")
            else:
                top = r.get("top") or r.get("reason")
                print(f"{r['label']} ({r['speaker_id']}): UNDECIDED  {top}")
    # Two speakers can never be the same person; flag it rather than hide it.
    chosen = [r["match"] for r in report if r.get("match")]
    for person, n in Counter(chosen).items():
        if n > 1:
            print(f"WARNING: {person} matched {n} speakers - diarization likely split one voice, check by hand")
    return 0


def cmd_list(args) -> int:
    library = Path(args.library)
    root = library / "people"
    if not root.is_dir():
        print("library is empty")
        return 0
    for d in sorted(root.iterdir()):
        manifest = d / "manifest.jsonl"
        meta = d / "person.json"
        if not manifest.exists() or not meta.exists():
            continue
        entries = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()]
        secs = sum(e["end"] - e["start"] for e in entries)
        sources = sorted({e["source"] for e in entries})
        person = json.loads(meta.read_text(encoding="utf-8"))["person"]
        print(f"{person}: {len(entries)} segment(s), {secs:.0f}s, {len(sources)} recording(s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n", 1)[0])
    ap.add_argument("--library", default=str(DEFAULT_LIBRARY), help="voice library folder (local, never a repo)")
    ap.add_argument("--model", help="speaker embedding ONNX model (default: <library>/models/" + DEFAULT_MODEL + ")")
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("map-labels", help="propose speaker_id -> person from a hand-labeled transcript")
    m.add_argument("--json", required=True, help="word-level transcript JSON of the recording")
    m.add_argument("--labeled", required=True, help="hand-labeled .txt of the same recording")
    m.add_argument("--min-purity", type=float, default=0.8)
    m.set_defaults(func=cmd_map_labels)

    e = sub.add_parser("enroll", help="add confident samples of known speakers to the library")
    e.add_argument("--audio", required=True)
    e.add_argument("--json", required=True)
    e.add_argument("--speaker", action="append", required=True, metavar="speaker_N=PERSON")
    e.add_argument("--max-segments", type=int, default=12, help="longest confident stretches kept per speaker")
    e.set_defaults(func=cmd_enroll)

    p = sub.add_parser("enroll-pair", help="two-person recording with one known voice: enroll the other, no transcript needed")
    p.add_argument("--audio", required=True)
    p.add_argument("--known", required=True, help="the already-enrolled participant")
    p.add_argument("--other", required=True, help="the other participant (from the file name / labels)")
    p.add_argument("--window", type=float, default=4.0)
    p.add_argument("--hop", type=float, default=3.0)
    p.add_argument("--min-rms", type=float, default=0.02)
    p.add_argument("--known-min", type=float, default=0.60, help="window counts as the known person at or above this")
    p.add_argument("--other-max", type=float, default=0.25, help="window counts as the other person at or below this")
    p.add_argument("--cohesion", type=float, default=0.55, help="min similarity to the other side's own centroid")
    p.add_argument("--min-windows", type=int, default=15)
    p.add_argument("--max-segments", type=int, default=12)
    p.add_argument("--one-sided", action="store_true",
                   help="the recording captured only the other participant; skip the known-voice presence check")
    p.set_defaults(func=cmd_enroll_pair)

    i = sub.add_parser("identify", help="match a recording's speakers against the library")
    i.add_argument("--audio", required=True)
    i.add_argument("--json", required=True)
    i.add_argument("--candidates", help="comma-separated people to consider (e.g. the meeting's invitees)")
    i.add_argument("--threshold", type=float, default=0.65, help="minimum cosine similarity to accept a match")
    i.add_argument("--margin", type=float, default=0.20, help="minimum lead over the runner-up")
    i.add_argument("--max-segments", type=int, default=12)
    i.add_argument("--json-out", action="store_true")
    i.set_defaults(func=cmd_identify)

    ls = sub.add_parser("list", help="show enrolled people")
    ls.set_defaults(func=cmd_list)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
