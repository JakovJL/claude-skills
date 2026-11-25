#!/usr/bin/env python3
"""Validate a portable requirement/criterion/test registry without running tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PureWindowsPath
import sys


def checked_file(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("path must be a nonempty relative string")
    relative = Path(value)
    windows = PureWindowsPath(value)
    if relative.is_absolute() or windows.drive or windows.root:
        raise ValueError("absolute or drive-relative paths are not allowed")
    if ".." in relative.parts or ".." in windows.parts:
        raise ValueError("parent traversal is not allowed")
    try:
        target = (root / relative).resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError("referenced file does not exist or cannot be resolved") from exc
    if not target.is_relative_to(root):
        raise ValueError("referenced path resolves outside the project root")
    if not target.is_file():
        raise ValueError("referenced path is not a regular file")
    return target


def validate_registry(data: object, root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    result = {"valid": False, "errors": errors, "warnings": warnings, "counts": {}}
    if not isinstance(data, dict):
        errors.append("registry must be a JSON object")
        return result

    collections: dict[str, dict[str, dict]] = {}
    seen: set[str] = set()
    for group in ("requirements", "acceptance_criteria", "tests"):
        rows = data.get(group)
        by_id: dict[str, dict] = {}
        collections[group] = by_id
        if not isinstance(rows, list):
            errors.append(f"{group} must be an array")
            continue
        for index, row in enumerate(rows):
            location = f"{group}[{index}]"
            if not isinstance(row, dict):
                errors.append(f"{location} must be an object")
                continue
            item_id = row.get("id")
            if not isinstance(item_id, str) or not item_id.strip() or item_id != item_id.strip():
                errors.append(f"{location}.id must be a nonempty string without surrounding whitespace")
                continue
            if item_id in seen:
                errors.append(f"duplicate id: {item_id}")
                continue
            seen.add(item_id)
            by_id[item_id] = row

    def links(item_id: str, row: dict, field: str, targets: dict[str, dict]) -> list[str]:
        values = row.get(field)
        if not isinstance(values, list) or not values:
            errors.append(f"{item_id}.{field} must be a nonempty array")
            return []
        linked: list[str] = []
        for index, value in enumerate(values):
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{item_id}.{field}[{index}] must be a nonempty ID")
            elif value not in targets:
                errors.append(f"{item_id}.{field} references unknown id: {value}")
            elif value in linked:
                warnings.append(f"{item_id}.{field} repeats id: {value}")
            else:
                linked.append(value)
        return linked

    requirements = collections["requirements"]
    criteria = collections["acceptance_criteria"]
    tests = collections["tests"]
    referenced_criteria: set[str] = set()
    referenced_tests: set[str] = set()
    for item_id, row in requirements.items():
        referenced_criteria.update(links(item_id, row, "criteria", criteria))
    for item_id, row in criteria.items():
        referenced_tests.update(links(item_id, row, "tests", tests))
    for item_id in sorted(set(criteria) - referenced_criteria):
        warnings.append(f"criterion is not linked to a requirement: {item_id}")
    for item_id in sorted(set(tests) - referenced_tests):
        warnings.append(f"test is not linked to a criterion: {item_id}")

    kinds = {"automated": 0, "manual": 0, "planned": 0}
    for item_id, row in tests.items():
        kind = row.get("kind")
        if not isinstance(kind, str) or kind not in kinds:
            errors.append(f"{item_id}.kind must be automated, manual or planned")
            continue
        kinds[kind] += 1
        if kind != "planned" or "path" in row:
            try:
                checked_file(root, row.get("path"))
            except ValueError as exc:
                errors.append(f"{item_id}.path: {exc}")

    result["counts"] = {
        "requirements": len(requirements),
        "acceptance_criteria": len(criteria),
        "tests": len(tests),
        "tests_by_kind": kinds,
    }
    result["valid"] = not errors
    return result


def reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON numbers are not supported")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    parser.add_argument("--root", type=Path, required=True, help="Project boundary for referenced files")
    parser.add_argument("--json", action="store_true", help="Print the structured result")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("--root must name an existing directory")
        data = json.loads(args.registry.read_text(encoding="utf-8-sig"), parse_constant=reject_constant)
    except (OSError, ValueError, RecursionError, RuntimeError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    report = validate_registry(data, root)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print("Traceability links: " + ("valid" if report["valid"] else "invalid"))
        print(json.dumps(report["counts"], ensure_ascii=True))
        for message in report["errors"]:
            print("ERROR: " + message)
        for message in report["warnings"]:
            print("WARNING: " + message)
        print("No tests were executed.")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
