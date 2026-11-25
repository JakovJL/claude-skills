"""Include the shipped media safety checks in repository test discovery."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


def load_tests(loader: unittest.TestLoader, _tests: unittest.TestSuite, _pattern: str | None):
    path = Path(__file__).resolve().parents[1] / "plugins/jakov-skills/skills/video-trim-and-audio-extract/scripts/test_video_tail_trim.py"
    spec = importlib.util.spec_from_file_location("packaged_media_checks", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load bundled media checks")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return loader.loadTestsFromModule(module)
