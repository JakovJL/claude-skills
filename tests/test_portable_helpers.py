"""Behavioral checks for the two portable, offline evidence validators."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "jakov-skills" / "skills"


def load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, SKILLS / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


trace = load("traceability_checker", "requirements-traceability/scripts/check_traceability.py")
replay = load("replay_checker", "llm-trace-replay/scripts/verify_replay.py")


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "scenario.md").write_text("Synthetic manual scenario", encoding="utf-8")

    def run_cli(self, script: Path, value: object):
        manifest = self.root / "input.json"
        manifest.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(script), str(manifest), "--root", str(self.root), "--json"],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=15,
        )


class TraceabilityTests(FixtureCase):
    def registry(self):
        return {
            "requirements": [{"id": "R-1", "criteria": ["AC-1"]}],
            "acceptance_criteria": [{"id": "AC-1", "tests": ["T-1", "T-2"]}],
            "tests": [
                {"id": "T-1", "kind": "manual", "path": "scenario.md"},
                {"id": "T-2", "kind": "planned"},
            ],
        }

    def test_manual_and_planned_links_are_counted_without_running_any_test(self):
        data = self.registry()
        report = trace.validate_registry(data, self.root)
        self.assertTrue(report["valid"])
        self.assertEqual(report["counts"]["tests_by_kind"], {"automated": 0, "manual": 1, "planned": 1})

    def test_unknown_reference_is_a_validation_failure(self):
        data = self.registry()
        data["acceptance_criteria"][0]["tests"].append("T-missing")
        self.assertFalse(trace.validate_registry(data, self.root)["valid"])

    def test_duplicate_ids_across_collections_are_rejected(self):
        data = self.registry()
        data["tests"][1]["id"] = "R-1"
        report = trace.validate_registry(data, self.root)
        self.assertIn("duplicate id: R-1", report["errors"])

    def test_missing_test_path_fails(self):
        data = self.registry()
        data["tests"][0]["path"] = "not-created.md"
        self.assertFalse(trace.validate_registry(data, self.root)["valid"])

    def test_paths_cannot_escape_or_use_windows_drive_relative_syntax(self):
        for value in ("../outside.md", "/outside.md", "C:/outside.md", "C:outside.md", "..\\outside.md"):
            with self.subTest(value=value):
                data = self.registry()
                data["tests"][0]["path"] = value
                self.assertFalse(trace.validate_registry(data, self.root)["valid"])

    def test_uncovered_criterion_fails(self):
        data = self.registry()
        data["acceptance_criteria"][0]["tests"] = []
        self.assertFalse(trace.validate_registry(data, self.root)["valid"])

    def test_bad_collection_or_kind_has_a_structured_error(self):
        for mutate in (
            lambda data: data.update(tests=None),
            lambda data: data["tests"][0].update(kind=[]),
        ):
            data = self.registry()
            mutate(data)
            self.assertFalse(trace.validate_registry(data, self.root)["valid"])

    def test_cli_exit_codes_distinguish_consistent_and_inconsistent_links(self):
        script = SKILLS / "requirements-traceability/scripts/check_traceability.py"
        passed = self.run_cli(script, self.registry())
        self.assertEqual(passed.returncode, 0, passed.stderr)
        self.assertTrue(json.loads(passed.stdout)["valid"])
        data = self.registry()
        data["requirements"][0]["criteria"] = ["unknown"]
        failed = self.run_cli(script, data)
        self.assertEqual(failed.returncode, 1)
        self.assertFalse(json.loads(failed.stdout)["valid"])


class ReplayTests(FixtureCase):
    def manifest(self):
        (self.root / "knowledge.md").write_text("Synthetic knowledge: пример", encoding="utf-8")
        messages = [{"role": "user", "content": "PRIVATE-SYNTHETIC-MARKER"}]
        settings = {"model": "fixture-model", "temperature": 0}
        return {
            "schema_version": 1,
            "cases": [{
                "id": "case-1",
                "messages": messages,
                "messages_sha256": replay.canonical_hash(messages),
                "settings": settings,
                "settings_sha256": replay.canonical_hash(settings),
                "knowledge": [{"path": "knowledge.md", "sha256": replay.file_hash(self.root / "knowledge.md")}],
            }],
        }

    def test_valid_fixture_checks_messages_settings_and_original_file_bytes(self):
        report = replay.verify_manifest(self.manifest(), self.root)
        self.assertTrue(report["valid"])
        self.assertEqual(report["knowledge_files_checked"], 1)

    def test_canonical_hash_keeps_unicode_and_list_order_but_ignores_object_key_order(self):
        self.assertEqual(replay.canonical_hash({"б": 2, "а": 1}), replay.canonical_hash({"а": 1, "б": 2}))
        self.assertNotEqual(replay.canonical_hash([1, 2]), replay.canonical_hash([2, 1]))

    def test_tampered_prompt_and_settings_fail_without_printing_values(self):
        for field in ("messages", "settings"):
            with self.subTest(field=field):
                data = self.manifest()
                if field == "messages":
                    data["cases"][0][field][0]["content"] += " changed"
                else:
                    data["cases"][0][field]["temperature"] = 1
                report = replay.verify_manifest(data, self.root)
                self.assertFalse(report["valid"])
                self.assertNotIn("PRIVATE-SYNTHETIC-MARKER", json.dumps(report))

    def test_knowledge_file_tampering_fails(self):
        data = self.manifest()
        (self.root / "knowledge.md").write_text("Changed", encoding="utf-8")
        self.assertFalse(replay.verify_manifest(data, self.root)["valid"])

    def test_knowledge_path_escape_fails(self):
        data = self.manifest()
        data["cases"][0]["knowledge"][0]["path"] = "../knowledge.md"
        self.assertFalse(replay.verify_manifest(data, self.root)["valid"])

    def test_settings_secrets_are_rejected_without_value_disclosure(self):
        data = self.manifest()
        settings = data["cases"][0]["settings"]
        settings["headers"] = {"Authorization": "DO-NOT-PRINT-THIS"}
        data["cases"][0]["settings_sha256"] = replay.canonical_hash(settings)
        report = replay.verify_manifest(data, self.root)
        self.assertFalse(report["valid"])
        self.assertNotIn("DO-NOT-PRINT-THIS", json.dumps(report))

    def test_duplicate_case_ids_and_invalid_schema_are_rejected(self):
        data = self.manifest()
        data["cases"].append(copy.deepcopy(data["cases"][0]))
        self.assertFalse(replay.verify_manifest(data, self.root)["valid"])
        data["schema_version"] = True
        self.assertFalse(replay.verify_manifest(data, self.root)["valid"])

    def test_cli_reports_only_integrity_and_uses_no_output_artifacts(self):
        data = self.manifest()
        before = set(self.root.iterdir())
        completed = self.run_cli(SKILLS / "llm-trace-replay/scripts/verify_replay.py", data)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("PRIVATE-SYNTHETIC-MARKER", completed.stdout + completed.stderr)
        self.assertEqual(set(self.root.iterdir()) - before, {self.root / "input.json"})

    def test_malformed_json_has_input_error_exit_code(self):
        path = self.root / "broken.json"
        path.write_text("{not JSON", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SKILLS / "llm-trace-replay/scripts/verify_replay.py"), str(path), "--root", str(self.root)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)

    def test_symlink_to_outside_root_is_rejected_when_host_allows_symlinks(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other) / "outside.md"
            outside.write_text("Not part of the fixture root", encoding="utf-8")
            link = self.root / "linked.md"
            try:
                os.symlink(outside, link)
            except OSError as exc:
                self.skipTest(f"host does not permit symlink creation: {exc}")
            data = self.manifest()
            data["cases"][0]["knowledge"][0] = {"path": "linked.md", "sha256": hashlib.sha256(outside.read_bytes()).hexdigest()}
            self.assertFalse(replay.verify_manifest(data, self.root)["valid"])


if __name__ == "__main__":
    unittest.main()
