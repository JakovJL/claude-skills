#!/usr/bin/env python3
"""Detect where real audio activity ends in a recording, trim the dead tail,
and extract an MP3 audio stream next to the source file.

Requires ffmpeg + ffprobe on PATH.

Subcommands:
  detect     FILE  analyse audio activity, print blocks and a suggested cut point
  cut        FILE  write <stem>_trimmed<ext>  (stream copy by default)
  audio      FILE  write <stem>_audio.mp3  (--for-stt for a 16 kHz upload copy)
  process    FILE  detect -> cut -> audio (audio taken from the trimmed file)
  transcribe FILE  upload to ElevenLabs Scribe, write a speaker-labeled
                   <stem>_transcript.txt  (--dry-run to see the request first)

`transcribe` is the only subcommand that touches the network. It uploads the
file it is given to a third party, so it never runs as part of `process`;
sending a recording off the machine is always an explicit, separate step.
"""

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

SILENCE_START_RE = re.compile(r"silence_start:\s*(-?[0-9.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*(-?[0-9.]+)")


def die(msg, code=2):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(code)


def need_tools():
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            die(
                tool + " not found on PATH. Install ffmpeg "
                "(Windows: choco install ffmpeg, macOS: brew install ffmpeg, "
                "Debian/Ubuntu: apt install ffmpeg) and retry."
            )


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", path],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if out.returncode != 0:
        die("ffprobe failed on " + path + ":\n" + out.stderr.strip())
    data = json.loads(out.stdout)
    audio = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    if not audio:
        die(path + " has no audio stream, nothing to detect.")
    duration = float(data.get("format", {}).get("duration") or 0.0)
    if duration <= 0:
        for s in data["streams"]:
            if s.get("duration"):
                duration = float(s["duration"])
                break
    return duration, audio[0]


def hms(seconds):
    if seconds is None:
        return "-"
    seconds = max(0.0, float(seconds))
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return "{:02d}:{:02d}:{:06.3f}".format(h, m, s)


def silence_intervals(path, noise_db, min_silence):
    """Return list of (start, end) silent intervals, per ffmpeg silencedetect."""
    cmd = [
        "ffmpeg", "-hide_banner", "-nostats", "-i", path,
        "-map", "0:a:0", "-vn",
        "-af", "silencedetect=noise={}dB:d={}".format(noise_db, min_silence),
        "-f", "null", "-",
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if proc.returncode != 0:
        die("ffmpeg silencedetect failed:\n" + proc.stderr[-2000:])
    intervals = []
    pending = None
    for line in proc.stderr.splitlines():
        m = SILENCE_START_RE.search(line)
        if m:
            pending = max(0.0, float(m.group(1)))
            continue
        m = SILENCE_END_RE.search(line)
        if m and pending is not None:
            intervals.append((pending, float(m.group(1))))
            pending = None
    if pending is not None:
        intervals.append((pending, None))  # runs to end of file
    return intervals


def active_segments(intervals, duration):
    """Invert silence intervals into active (non-silent) segments."""
    segs = []
    cursor = 0.0
    for start, end in intervals:
        if start > cursor:
            segs.append((cursor, min(start, duration)))
        cursor = duration if end is None else max(cursor, end)
    if cursor < duration:
        segs.append((cursor, duration))
    return [(a, b) for a, b in segs if b - a > 0.01]


def build_blocks(segs, merge_gap):
    """Merge active segments separated by gaps < merge_gap into blocks."""
    blocks = []
    for a, b in segs:
        if blocks and a - blocks[-1]["end"] < merge_gap:
            blocks[-1]["end"] = b
            blocks[-1]["active"] += b - a
            blocks[-1]["segments"] += 1
        else:
            blocks.append({"start": a, "end": b, "active": b - a, "segments": 1})
    for blk in blocks:
        span = blk["end"] - blk["start"]
        blk["span"] = span
        blk["density"] = blk["active"] / span if span > 0 else 0.0
    return blocks


def classify(blocks, min_content, min_density):
    for blk in blocks:
        blk["content"] = blk["active"] >= min_content and blk["density"] >= min_density
    return blocks


def analyse(path, args):
    duration, astream = probe(path)
    intervals = silence_intervals(path, args.noise_db, args.min_silence)
    segs = active_segments(intervals, duration)
    blocks = classify(
        build_blocks(segs, args.merge_gap), args.min_content, args.min_density
    )
    content = [b for b in blocks if b["content"]]
    cut_at = None
    if content:
        cut_at = min(duration, content[-1]["end"] + args.pad)
    return {
        "path": path,
        "duration": duration,
        "audio_codec": astream.get("codec_name"),
        "blocks": blocks,
        "content_blocks": content,
        "cut_at": cut_at,
    }


def print_report(rep, args):
    print("file            : " + rep["path"])
    print("duration        : {}  ({:.1f}s)".format(hms(rep["duration"]),
                                                   rep["duration"]))
    print("audio codec     : {}".format(rep["audio_codec"]))
    print("thresholds      : noise={}dB min_silence={}s merge_gap={}s "
          "min_content={}s min_density={}".format(
              args.noise_db, args.min_silence, args.merge_gap,
              args.min_content, args.min_density))
    print()
    print("{:>3}  {:>12}  {:>12}  {:>10}  {:>10}  {:>5}  verdict".format(
        "#", "start", "end", "span", "sound", "dens"))
    for i, b in enumerate(rep["blocks"], 1):
        print("{:>3}  {:>12}  {:>12}  {:>9.1f}s  {:>9.1f}s  {:>5.2f}  {}".format(
            i, hms(b["start"]), hms(b["end"]), b["span"], b["active"],
            b["density"], "CONTENT" if b["content"] else "noise/idle"))
    print()
    if rep["cut_at"] is None:
        print("no content block found - loosen --min-content / --min-density, "
              "or move --noise-db closer to 0 if the room is loud")
    else:
        last = rep["content_blocks"][-1]
        tail = rep["duration"] - rep["cut_at"]
        print("last content ends : " + hms(last["end"]))
        print("suggested cut at  : {}  (includes {}s pad)".format(
            hms(rep["cut_at"]), args.pad))
        print("tail discarded    : {}  ({:.1f} min)".format(hms(tail), tail / 60))


def out_path(path, suffix, ext=None):
    stem, orig_ext = os.path.splitext(path)
    return stem + suffix + (ext or orig_ext)


def guard_overwrite(dest, force):
    if os.path.exists(dest) and not force:
        die(dest + " already exists. Pass --force to overwrite.")


def same_file(left, right):
    if os.path.normcase(os.path.realpath(left)) == os.path.normcase(os.path.realpath(right)):
        return True
    try:
        return os.path.samefile(left, right)
    except (OSError, ValueError):
        return False


def guard_output(source, dest, force, original=None):
    if same_file(source, dest) or (original and same_file(original, dest)):
        die("output must be a different file from the source: " + dest)
    guard_overwrite(dest, force)


def run_ffmpeg(cmd, what):
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if proc.returncode != 0:
        die(what + " failed:\n" + proc.stderr[-2000:])


def do_cut(path, start, end, args):
    dest = args.output or out_path(path, args.suffix)
    guard_output(path, dest, args.force)
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-y" if args.force else "-n"]
    if start:
        cmd += ["-ss", "{:.3f}".format(start)]
    cmd += ["-i", path]
    if end is not None:
        cmd += ["-to", "{:.3f}".format(end - start if start else end)]
    if args.reencode:
        cmd += ["-c:v", "libx264", "-crf", "20", "-preset", "medium",
                "-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-c", "copy", "-avoid_negative_ts", "make_zero"]
    cmd += [dest]
    run_ffmpeg(cmd, "ffmpeg cut")
    print("wrote video : " + dest)
    return dest


def do_audio(path, args, start=0.0, end=None):
    """Extract mp3. With start/end set, only that range - the audio is
    re-encoded anyway, so seeking before -i is both fast and sample-accurate;
    no keyframe snapping applies as it would to a stream-copied video."""
    dest = args.audio_output or out_path(path, args.audio_suffix, ".mp3")
    guard_output(path, dest, args.force, getattr(args, "source_path", None))
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-y" if args.force else "-n"]
    if start:
        cmd += ["-ss", "{:.3f}".format(start)]
    cmd += ["-i", path]
    if end is not None:
        cmd += ["-t", "{:.3f}".format(end - start)]
    cmd += ["-vn", "-map", "0:a:0", "-c:a", "libmp3lame"]
    if getattr(args, "for_stt", False):
        # A compact transcription copy; the caller selects this preset only
        # when 16 kHz mono is suitable for the selected downstream model.
        cmd += ["-ar", "16000", "-ac", "1"]
        if args.bitrate:
            cmd += ["-b:a", args.bitrate]
    else:
        if args.bitrate:
            cmd += ["-b:a", args.bitrate]
        else:
            cmd += ["-q:a", str(args.quality)]
        if args.mono:
            cmd += ["-ac", "1"]
    cmd += [dest]
    run_ffmpeg(cmd, "ffmpeg mp3 extraction")
    print("wrote audio : " + dest)
    return dest


def parse_time(value):
    if value is None:
        return None
    value = str(value).strip()
    if ":" in value:
        total = 0.0
        for part in value.split(":"):
            total = total * 60 + float(part)
        return total
    return float(value)


# ------------------------------------------------------------- transcription

STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"


def load_api_key(args):
    """Read the key from --api-key-file, else the ELEVENLABS_API_KEY env var.

    Deliberately never accepted as a command-line argument, so it cannot end
    up in shell history or in another user's `ps` output.
    """
    if args.api_key_file:
        path = os.path.expanduser(args.api_key_file)
        if not os.path.isfile(path):
            die("no such api key file: " + path)
        with io.open(path, encoding="utf-8") as fh:
            raw = fh.read().strip()
        if raw.startswith("{"):
            data = json.loads(raw)
            for field in ("api_key", "key", "xi_api_key"):
                if data.get(field):
                    return data[field].strip()
            die(path + " is JSON but has no api_key/key/xi_api_key field.")
        if not raw:
            die(path + " is empty.")
        return raw
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        die("no API key. Set ELEVENLABS_API_KEY, or pass --api-key-file "
            "pointing at a file holding the key (raw, or JSON with an "
            "api_key field).")
    return key


def build_multipart(fields, file_field, file_path):
    """Minimal multipart/form-data encoder, keeping this script stdlib-only."""
    boundary = "----videoTailTrim" + uuid.uuid4().hex
    sep = ("--" + boundary).encode()
    out = bytearray()
    for name, value in fields.items():
        if value is None:
            continue
        out += sep + b"\r\n"
        out += ('Content-Disposition: form-data; name="%s"\r\n\r\n'
                % name).encode()
        out += str(value).encode("utf-8") + b"\r\n"
    out += sep + b"\r\n"
    out += ('Content-Disposition: form-data; name="%s"; filename="%s"\r\n'
            % (file_field, os.path.basename(file_path))).encode("utf-8")
    out += b"Content-Type: application/octet-stream\r\n\r\n"
    with open(file_path, "rb") as fh:
        out += fh.read()
    out += b"\r\n" + sep + b"--\r\n"
    return bytes(out), "multipart/form-data; boundary=" + boundary


def words_to_turns(words):
    """Group consecutive words by speaker into readable turns.

    Speakers are numbered in order of first appearance so the labels are
    stable within a file, even though the API's own speaker ids are opaque.
    """
    turns = []
    order = {}
    for w in words:
        text = w.get("text", "")
        if not text:
            continue
        spk = w.get("speaker_id") or "speaker_0"
        if spk not in order:
            order[spk] = len(order) + 1
        label = "Speaker %d" % order[spk]
        if turns and turns[-1][0] == label:
            turns[-1][1].append(text)
        else:
            turns.append([label, [text], w.get("start")])
    return [(lbl, "".join(parts).strip(), start) for lbl, parts, start in turns]


def do_transcribe(path, args):
    dest = args.transcript_output or out_path(path, args.transcript_suffix,
                                              ".txt")
    guard_output(path, dest, args.force)
    jdest = out_path(path, args.transcript_suffix, ".json") if args.save_json else None
    if jdest:
        guard_output(path, jdest, args.force)
        if same_file(dest, jdest):
            die("transcript and raw JSON must use different output files")
    size_mb = os.path.getsize(path) / (1024 * 1024)

    fields = {
        "model_id": args.model,
        "diarize": "false" if args.no_diarize else "true",
        "language_code": args.language,
        "timestamps_granularity": "word",
    }
    if args.speakers:
        # Upper bound on speakers. Worth passing when the count is known,
        # and it is what a comparable UI ("How many speakers?") asks for.
        fields["num_speakers"] = args.speakers
    if args.no_verbatim:
        fields["no_verbatim"] = "true"

    if args.dry_run:
        print("DRY RUN - nothing is uploaded and no key is read")
        print("  endpoint   : POST " + STT_URL)
        print("  file       : %s  (%.1f MB)" % (path, size_mb))
        for key_name, value in fields.items():
            if value is not None:
                print("  %-11s: %s" % (key_name, value))
        print("  transcript : " + dest)
        return dest

    key = load_api_key(args)
    body, content_type = build_multipart(fields, "file", path)
    req = urllib.request.Request(STT_URL, data=body, method="POST")
    # xi-api-key only. Sending Authorization as well is a hard 401:
    # "Only one of xi-api-key and authorization headers must be provided."
    # Verified against the live API, not assumed.
    req.add_header("xi-api-key", key)
    req.add_header("Content-Type", content_type)

    print("uploading %.1f MB (model=%s, diarize=%s) ..."
          % (size_mb, args.model, fields["diarize"]))
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:1500]
        die("transcription failed: HTTP %s\n%s" % (exc.code, detail))
    except urllib.error.URLError as exc:
        die("could not reach the API: %s" % exc.reason)

    if args.save_json:
        with io.open(jdest, "w" if args.force else "x", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False, indent=2))
        print("wrote raw json   : " + jdest)

    words = payload.get("words") or []
    if words:
        turns = words_to_turns(words)
        speakers = len({t[0] for t in turns})
        lines = []
        for label, text, start in turns:
            stamp = ""
            if args.timestamps and start is not None:
                stamp = "[%s] " % hms(start)
            lines.append("%s%s: %s" % (stamp, label, text))
        note = "%d turns, %d speaker(s)" % (len(turns), speakers)
    else:
        plain = payload.get("text", "")
        if not plain:
            die("the API returned neither words nor text; re-run with "
                "--save-json to inspect the raw response.")
        lines = [plain]
        note = "no speaker data returned (diarization off or unsupported)"

    with io.open(dest, "w" if args.force else "x", encoding="utf-8", newline="\n") as fh:
        fh.write("\n\n".join(lines) + "\n")
    print("wrote transcript : %s  (%s)" % (dest, note))
    return dest


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def detection_args(sp):
        sp.add_argument("--noise-db", type=float, default=-32.0,
                        help="silence threshold in dBFS (default -32; "
                             "closer to 0 counts more as silence)")
        sp.add_argument("--min-silence", type=float, default=1.0,
                        help="shortest gap counted as silence, seconds "
                             "(default 1.0)")
        sp.add_argument("--merge-gap", type=float, default=20.0,
                        help="gaps shorter than this stay inside one block, "
                             "seconds (default 20)")
        sp.add_argument("--min-content", type=float, default=45.0,
                        help="a content block needs this much actual sound, "
                             "seconds (default 45)")
        sp.add_argument("--min-density", type=float, default=0.30,
                        help="a content block needs this sound/span ratio "
                             "(default 0.30); stray clicks score far lower")
        sp.add_argument("--pad", type=float, default=2.0,
                        help="seconds kept after the last content (default 2)")

    def cut_args(sp):
        sp.add_argument("--suffix", default="_trimmed")
        sp.add_argument("--output", help="explicit output video path")
        sp.add_argument("--reencode", action="store_true",
                        help="re-encode instead of stream copy (use when a "
                             "non-zero --start must land frame-exact)")

    def audio_args(sp):
        sp.add_argument("--audio-suffix", default="_audio")
        sp.add_argument("--audio-output", help="explicit output mp3 path")
        sp.add_argument("--quality", type=int, default=2,
                        help="libmp3lame VBR quality 0-9, lower is better "
                             "(default 2, about 190 kbps)")
        sp.add_argument("--bitrate",
                        help="fixed CBR bitrate, e.g. 128k (overrides --quality)")
        sp.add_argument("--mono", action="store_true",
                        help="downmix to mono, good for speech")
        sp.add_argument("--for-stt", action="store_true",
                        help="16 kHz mono preset for speech-to-text upload; "
                             "~75%% smaller than the default with no accuracy "
                             "cost, since STT engines resample to 16 kHz anyway")

    sp = sub.add_parser("detect", help="analyse only, write nothing")
    sp.add_argument("file")
    detection_args(sp)

    sp = sub.add_parser("cut", help="trim the file")
    sp.add_argument("file")
    sp.add_argument("--start", help="start time (s or HH:MM:SS), default 0")
    sp.add_argument("--end", help="end time (s or HH:MM:SS); "
                                  "omit to auto-detect the content end")
    detection_args(sp)
    cut_args(sp)
    sp.add_argument("--force", action="store_true")

    sp = sub.add_parser("audio", help="extract mp3 only")
    sp.add_argument("file")
    sp.add_argument("--start", help="start time (s or HH:MM:SS), default 0")
    sp.add_argument("--end", help="end time (s or HH:MM:SS); "
                                  "omit to extract the whole file")
    audio_args(sp)
    sp.add_argument("--force", action="store_true")

    sp = sub.add_parser("transcribe",
                        help="upload to ElevenLabs Scribe, write a "
                             "speaker-labeled transcript")
    sp.add_argument("file", help="audio (or video) file to upload; run "
                                 "`audio --for-stt` first for a small upload copy")
    sp.add_argument("--model", default="scribe_v2",
                    help="ElevenLabs model id (default scribe_v2; "
                         "scribe_v1 is the older model)")
    sp.add_argument("--language",
                    help="ISO code, e.g. ru or en. Omit to let the API "
                         "detect it")
    sp.add_argument("--no-diarize", action="store_true",
                    help="turn speaker labels off (they are on by default; "
                         "1:1 analysis needs them)")
    sp.add_argument("--speakers", type=int, metavar="N",
                    help="expected number of speakers (max 32). Pass it when "
                         "you know the count; it helps the model predict who "
                         "speaks when")
    sp.add_argument("--no-verbatim", action="store_true",
                    help="drop filler sounds and stutters for a cleaner read "
                         "(scribe_v2 only); omit to keep a verbatim record")
    sp.add_argument("--timestamps", action="store_true",
                    help="prefix each turn with its start time")
    sp.add_argument("--api-key-file",
                    help="file holding the API key, raw or JSON with an "
                         "api_key field. Otherwise ELEVENLABS_API_KEY is used")
    sp.add_argument("--transcript-suffix", default="_transcript")
    sp.add_argument("--transcript-output", help="explicit output .txt path")
    sp.add_argument("--save-json", action="store_true",
                    help="also write the raw API response next to the "
                         "transcript, for inspecting word-level data")
    sp.add_argument("--timeout", type=int, default=1800,
                    help="seconds to wait for the API (default 1800)")
    sp.add_argument("--dry-run", action="store_true",
                    help="print the request that would be sent and exit; "
                         "uploads nothing and reads no key")
    sp.add_argument("--force", action="store_true")

    sp = sub.add_parser("process", help="detect, cut, then extract mp3")
    sp.add_argument("file")
    sp.add_argument("--start", help="start time (s or HH:MM:SS), default 0")
    sp.add_argument("--end", help="override the auto-detected end")
    sp.add_argument("--audio-from", choices=["trimmed", "source"],
                    default="trimmed",
                    help="which file the mp3 comes from (default trimmed)")
    detection_args(sp)
    cut_args(sp)
    audio_args(sp)
    sp.add_argument("--force", action="store_true")

    args = p.parse_args()

    path = os.path.abspath(args.file)
    if not os.path.isfile(path):
        die("no such file: " + path)
    args.source_path = path

    if args.cmd == "transcribe":
        do_transcribe(path, args)
        return

    need_tools()

    if args.cmd == "audio":
        a_start = parse_time(args.start) or 0.0
        a_end = parse_time(args.end)
        if a_end is not None and a_end <= a_start:
            die("end ({}) must be greater than start ({}).".format(a_end, a_start))
        do_audio(path, args, a_start, a_end)
        return

    if args.cmd == "detect":
        print_report(analyse(path, args), args)
        return

    start = parse_time(getattr(args, "start", None)) or 0.0
    end = parse_time(getattr(args, "end", None))
    if end is None:
        rep = analyse(path, args)
        print_report(rep, args)
        print()
        if rep["cut_at"] is None:
            die("auto-detection found no content block; pass --end explicitly.")
        end = rep["cut_at"]
    if end <= start:
        die("end ({}) must be greater than start ({}).".format(end, start))

    trimmed = do_cut(path, start, end, args)
    if args.cmd == "process":
        # name the mp3 after the ORIGINAL file, not the _trimmed intermediate
        if not args.audio_output:
            args.audio_output = out_path(path, args.audio_suffix, ".mp3")
        do_audio(trimmed if args.audio_from == "trimmed" else path, args)


if __name__ == "__main__":
    main()
