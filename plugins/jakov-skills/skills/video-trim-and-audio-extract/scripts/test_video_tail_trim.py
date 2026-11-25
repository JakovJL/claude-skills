"""Local regression checks; uses synthetic files and mocked HTTP only.

Run from any working directory with:
    python /path/to/this/skill/scripts/test_video_tail_trim.py
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent


def load_helper(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


media = load_helper("video_tail_trim")
speaker = load_helper("speaker_voice_library")


class MediaHelperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="media-helper-test-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.source = self.folder / "fixture.wav"
        self.source.write_bytes(b"synthetic-fixture-not-a-recording")
        self.original_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def tearDown(self):
        self.assertEqual(
            hashlib.sha256(self.source.read_bytes()).hexdigest(), self.original_hash
        )

    def args(self, **changes):
        values = dict(
            transcript_output=None,
            transcript_suffix="_transcript",
            save_json=False,
            force=False,
            model="synthetic-model",
            no_diarize=False,
            language="en",
            speakers=None,
            no_verbatim=False,
            dry_run=True,
            timestamps=False,
            timeout=1,
            api_key_file=None,
        )
        values.update(changes)
        return SimpleNamespace(**values)

    def assert_refused(self, callback):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            callback()
        self.assertEqual(raised.exception.code, 2)

    def test_time_range_parsing(self):
        self.assertEqual(media.parse_time("01:02:03.5"), 3723.5)
        self.assertEqual(media.parse_time("12.25"), 12.25)

    def test_activity_is_inverted_from_silence(self):
        self.assertEqual(
            media.active_segments([(5, 10), (20, 25)], 30),
            [(0.0, 5), (10, 20), (25, 30)],
        )

    def test_sparse_activity_does_not_pass_content_threshold(self):
        blocks = media.classify(
            media.build_blocks([(0, 10), (12, 20), (50, 51)], 3), 15, 0.5
        )
        self.assertTrue(blocks[0]["content"])
        self.assertFalse(blocks[1]["content"])

    def test_turn_labels_follow_first_appearance(self):
        turns = media.words_to_turns([
            {"text": "Hello", "speaker_id": "b", "start": 0},
            {"text": " world", "speaker_id": "b", "start": 1},
            {"text": "Yes", "speaker_id": "a", "start": 2},
        ])
        self.assertEqual(turns, [("Speaker 1", "Hello world", 0), ("Speaker 2", "Yes", 2)])

    def test_source_output_is_refused_even_with_force(self):
        self.assert_refused(
            lambda: media.guard_output(str(self.source), str(self.source), True)
        )

    def test_normalized_source_alias_is_refused(self):
        alias = self.folder / ".." / self.folder.name / self.source.name
        self.assert_refused(
            lambda: media.guard_output(str(self.source), str(alias), True)
        )

    def test_source_hardlink_is_refused(self):
        alias = self.folder / "hardlink.wav"
        try:
            os.link(self.source, alias)
        except (OSError, NotImplementedError) as exc:
            self.skipTest("hard links unavailable: " + str(exc))
        self.assert_refused(
            lambda: media.guard_output(str(self.source), str(alias), True)
        )

    def test_original_source_is_protected_after_trimmed_intermediate(self):
        trimmed = self.folder / "trimmed.wav"
        trimmed.write_bytes(b"synthetic-intermediate")
        self.assert_refused(
            lambda: media.guard_output(
                str(trimmed), str(self.source), True, str(self.source)
            )
        )

    def test_existing_json_is_refused_before_credentials_or_network(self):
        sidecar = self.folder / "fixture_transcript.json"
        sidecar.write_text("do not replace", encoding="utf-8")
        with patch.object(media, "load_api_key", side_effect=AssertionError("key read")), patch.object(
            media.urllib.request, "urlopen", side_effect=AssertionError("network attempted")
        ):
            self.assert_refused(
                lambda: media.do_transcribe(str(self.source), self.args(save_json=True))
            )
        self.assertEqual(sidecar.read_text(encoding="utf-8"), "do not replace")

    def test_dry_run_reads_no_key_calls_no_network_and_writes_no_output(self):
        with patch.object(media, "load_api_key", side_effect=AssertionError("key read")), patch.object(
            media.urllib.request, "urlopen", side_effect=AssertionError("network attempted")
        ), contextlib.redirect_stdout(io.StringIO()) as output:
            destination = media.do_transcribe(str(self.source), self.args())
        self.assertIn("nothing is uploaded", output.getvalue())
        self.assertFalse(Path(destination).exists())

    def test_cli_dry_run_needs_neither_key_nor_ffmpeg_on_path(self):
        environment = dict(os.environ)
        environment.pop("ELEVENLABS_API_KEY", None)
        environment["PATH"] = ""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "video_tail_trim.py"), "transcribe",
             str(self.source), "--dry-run"],
            capture_output=True, text=True, encoding="utf-8", env=environment,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("no key is read", result.stdout)

    def test_force_replaces_outputs_with_mocked_provider_response(self):
        destination = self.folder / "fixture_transcript.txt"
        sidecar = self.folder / "fixture_transcript.json"
        destination.write_text("old transcript", encoding="utf-8")
        sidecar.write_text("old JSON", encoding="utf-8")
        payload = {"words": [{"text": "Synthetic response", "speaker_id": "s0", "start": 0}]}
        response = io.BytesIO(json.dumps(payload).encode("utf-8"))
        with patch.object(media, "load_api_key", return_value="synthetic-not-a-credential"), patch.object(
            media.urllib.request, "urlopen", return_value=response
        ) as request, contextlib.redirect_stdout(io.StringIO()):
            media.do_transcribe(
                str(self.source), self.args(force=True, save_json=True, dry_run=False)
            )
        self.assertEqual(request.call_count, 1)
        self.assertIn("Synthetic response", destination.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(sidecar.read_text(encoding="utf-8")), payload)

    def test_speaker_parser_uses_supplied_anonymous_labels_only(self):
        source = self.folder / "synthetic.json"
        source.write_text(json.dumps({"words": [
            {"type": "word", "speaker_id": "s1", "start": 0, "end": 4, "text": "One"},
            {"type": "word", "speaker_id": "s2", "start": 5, "end": 9, "text": "Two"},
        ]}), encoding="utf-8")
        self.assertEqual(speaker.speaker_order(speaker.load_turns(source)), ["s1", "s2"])


if __name__ == "__main__":
    unittest.main()
