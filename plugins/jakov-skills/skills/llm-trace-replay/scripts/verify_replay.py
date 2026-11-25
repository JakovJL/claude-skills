#!/usr/bin/env python3
"""Verify frozen LLM fixture hashes offline; never contact a provider."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys


SECRET_KEYS = {
    "api_key", "apikey", "authorization", "access_token", "refresh_token",
    "password", "client_secret", "cookie", "cookies", "secret_key", "bearer_token",
}


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checked_file(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("knowledge path must be a nonempty relative string")
    relative = Path(value)
    windows = PureWindowsPath(value)
    if relative.is_absolute() or windows.drive or windows.root:
        raise ValueError("absolute or drive-relative knowledge paths are not allowed")
    if ".." in relative.parts or ".." in windows.parts:
        raise ValueError("parent traversal in knowledge paths is not allowed")
    try:
        target = (root / relative).resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError("knowledge file does not exist or cannot be resolved") from exc
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError("knowledge path must resolve to a regular file inside the fixture root")
    return target


def sensitive_keys(value: object, prefix: str = "settings") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            location = f"{prefix}.{key}"
            if normalized in SECRET_KEYS:
                found.append(location)
            else:
                found.extend(sensitive_keys(child, location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(sensitive_keys(child, f"{prefix}[{index}]"))
    return found


def verify_manifest(data: object, root: Path) -> dict:
    errors: list[str] = []
    report = {"valid": False, "cases": [], "knowledge_files_checked": 0, "errors": errors}
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        errors.append("manifest must be an object with schema_version 1")
        return report
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("cases must be a nonempty array")
        return report
    seen: set[str] = set()

    def check_hash(case_id: str, field: str, value: object, expected: object) -> None:
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
            errors.append(f"{case_id}: {field}_sha256 must contain 64 hexadecimal characters")
            return
        try:
            actual = canonical_hash(value)
        except (ValueError, TypeError, RecursionError):
            errors.append(f"{case_id}: {field} is not canonical JSON")
            return
        if actual != expected.lower():
            errors.append(f"{case_id}: {field} hash mismatch")

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"cases[{index}] must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip() or case_id != case_id.strip():
            errors.append(f"cases[{index}].id must be a nonempty string without surrounding whitespace")
            continue
        if case_id in seen:
            errors.append(f"duplicate case id: {case_id}")
            continue
        seen.add(case_id)
        report["cases"].append(case_id)
        messages = case.get("messages")
        if not isinstance(messages, list) or not messages or any(
            not isinstance(message, dict)
            or not isinstance(message.get("role"), str)
            or not message["role"].strip()
            for message in messages
        ):
            errors.append(f"{case_id}: messages must be a nonempty array of objects with string roles")
        check_hash(case_id, "messages", messages, case.get("messages_sha256"))
        settings = case.get("settings")
        if not isinstance(settings, dict):
            errors.append(f"{case_id}: settings must be an object")
        else:
            for location in sensitive_keys(settings):
                errors.append(f"{case_id}: secret-bearing field is not allowed at {location}")
        check_hash(case_id, "settings", settings, case.get("settings_sha256"))
        knowledge = case.get("knowledge", [])
        if not isinstance(knowledge, list):
            errors.append(f"{case_id}: knowledge must be an array")
            continue
        for entry_index, entry in enumerate(knowledge):
            location = f"{case_id}: knowledge[{entry_index}]"
            if not isinstance(entry, dict):
                errors.append(f"{location} must be an object")
                continue
            expected = entry.get("sha256")
            if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
                errors.append(f"{location}.sha256 must contain 64 hexadecimal characters")
                continue
            try:
                target = checked_file(root, entry.get("path"))
                actual = file_hash(target)
            except (ValueError, OSError) as exc:
                errors.append(f"{location}: {exc}")
                continue
            report["knowledge_files_checked"] += 1
            if actual != expected.lower():
                errors.append(f"{location}: file hash mismatch")
    report["valid"] = not errors
    return report


def reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON numbers are not supported")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, required=True, help="Boundary containing knowledge fixture files")
    parser.add_argument("--json", action="store_true", help="Print the structured integrity result")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("--root must name an existing directory")
        data = json.loads(args.manifest.read_text(encoding="utf-8-sig"), parse_constant=reject_constant)
        report = verify_manifest(data, root)
    except (OSError, ValueError, RuntimeError, RecursionError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print("Replay fixture integrity: " + ("valid" if report["valid"] else "invalid"))
        print(f"Cases: {len(report['cases'])}; knowledge files checked: {report['knowledge_files_checked']}")
        for error in report["errors"]:
            print("ERROR: " + error)
        print("No credentials loaded, provider calls made or results written.")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
