#!/usr/bin/env python3
"""Check marketplace structure, skill discovery, resource links and Python syntax."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    raise SystemExit("Repository validation requires PyYAML; runtime helpers use the standard library.")


EXCLUDED = {"candidate-legend", "candidate-legend-description", "candidate-legend-questions"}
PRIVATE_MARKERS = re.compile(r"(?i)(?:[A-Z]:[\\/]Users[\\/](?!example\b|user\b|<)|\bYakau\b|\bFrontetica\b|innowise\.com)")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---(?:\n|\Z)", re.S)
LINK = re.compile(r"\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)")
RESOURCE = re.compile(r"(?<![\w/])((?:references|scripts|assets|evals)/[\w./-]+\.(?:md|py|ps1|json|yaml|yml|png|jpg|html|lua))\b")


def without_fences(text: str) -> str:
    output = []
    fence: str | None = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)[0]
            fence = None if fence == marker else marker if fence is None else fence
        elif fence is None:
            output.append(line)
    return "\n".join(output)


def validate(root: Path) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    counts: dict[str, int] = {}
    names: set[str] = set()

    def fail(path: Path, message: str):
        errors.append(f"{path.relative_to(root).as_posix()}: {message}")

    def read_json(path: Path):
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            fail(path, f"invalid or missing JSON ({exc})")
            return None

    marketplace_path = root / ".claude-plugin/marketplace.json"
    marketplace = read_json(marketplace_path)
    if not isinstance(marketplace, dict) or not isinstance(marketplace.get("plugins"), list):
        return errors + ["marketplace must contain a plugins array"], counts

    plugin_names: set[str] = set()
    registered: set[Path] = set()
    for entry in marketplace["plugins"]:
        if not isinstance(entry, dict):
            fail(marketplace_path, "plugin entry must be an object")
            continue
        name, source = entry.get("name"), entry.get("source")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            fail(marketplace_path, "plugin name is missing or invalid")
            continue
        if name in plugin_names:
            fail(marketplace_path, f"duplicate plugin: {name}")
        plugin_names.add(name)
        if not isinstance(source, str) or not source.startswith("./plugins/"):
            fail(marketplace_path, f"{name}: source must be a local ./plugins/ directory")
            continue
        plugin = (root / source).resolve()
        if not plugin.is_relative_to(root / "plugins") or not plugin.is_dir():
            fail(marketplace_path, f"{name}: source escapes plugins or is missing")
            continue
        registered.add(plugin)
        manifest_path = plugin / ".claude-plugin/plugin.json"
        manifest = read_json(manifest_path)
        if not isinstance(manifest, dict) or manifest.get("name") != name:
            fail(manifest_path, "manifest name must match the marketplace entry")
        elif not isinstance(manifest.get("version"), str) or not re.fullmatch(r"\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?", manifest["version"]):
            fail(manifest_path, "explicit semantic version is required")

        skill_paths = sorted((plugin / "skills").glob("*/SKILL.md"))
        counts[name] = len(skill_paths)
        if not skill_paths:
            fail(manifest_path, "plugin has no discovered skill entrypoints")
        for skill_path in skill_paths:
            content = skill_path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
            match = FRONTMATTER.match(content)
            if not match:
                fail(skill_path, "missing or malformed frontmatter")
                continue
            try:
                meta = yaml.safe_load(match.group(1))
            except yaml.YAMLError as exc:
                fail(skill_path, f"invalid YAML ({exc})")
                continue
            if not isinstance(meta, dict):
                fail(skill_path, "frontmatter must be a mapping")
                continue
            skill_name = meta.get("name")
            description = meta.get("description")
            if not isinstance(skill_name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_name) or len(skill_name) > 64:
                fail(skill_path, "invalid skill name")
                continue
            if skill_name != skill_path.parent.name:
                fail(skill_path, "folder name differs from frontmatter name")
            if skill_name in names:
                fail(skill_path, "skill name appears more than once")
            names.add(skill_name)
            if skill_name in EXCLUDED:
                fail(skill_path, "excluded candidate-legend family is present")
            if not isinstance(description, str) or not description.strip() or len(description) > 1024:
                fail(skill_path, "description must be nonempty and at most 1024 characters")
            if not content[match.end():].strip():
                fail(skill_path, "skill instructions are empty")

        for path in sorted(plugin.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.suffix.lower() not in {".md", ".py", ".json", ".ps1", ".yaml", ".yml", ".lua", ".html"}:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                fail(path, f"resource is not readable UTF-8 ({exc})")
                continue
            if PRIVATE_MARKERS.search(text):
                fail(path, "personal/local-machine marker requires review")
            if path.suffix == ".py":
                try:
                    ast.parse(text, filename=str(path))
                except SyntaxError as exc:
                    fail(path, f"Python syntax error at line {exc.lineno}: {exc.msg}")
            if path.suffix != ".md":
                continue
            skill = next((parent for parent in path.parents if (parent / "SKILL.md").is_file()), None)
            if skill is None:
                continue
            candidates: list[tuple[str, Path]] = []
            for match in LINK.finditer(without_fences(text)):
                target = match.group(1).strip().strip("<>")
                if re.search(r'\s+["\']', target):
                    target = re.split(r'\s+["\']', target, maxsplit=1)[0]
                if not target or target.startswith("#") or urlsplit(target).scheme:
                    continue
                candidates.append((target, path.parent))
            for match in RESOURCE.finditer(text):
                candidates.append((match.group(1), skill))
            for target, base in candidates:
                expanded = target.replace("${CLAUDE_SKILL_DIR}", str(skill)).replace("${CLAUDE_PLUGIN_ROOT}", str(plugin))
                expanded = unquote(expanded.split("#", 1)[0].split("?", 1)[0])
                resolved = (base / expanded).resolve()
                if not resolved.is_relative_to(plugin):
                    fail(path, f"resource leaves its plugin: {target}")
                elif not resolved.exists():
                    fail(path, f"missing resource: {target}")

    for path in (root / "plugins").iterdir():
        if path.is_dir() and path.resolve() not in registered:
            fail(path, "plugin directory is not registered in marketplace")
    return sorted(set(errors)), counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors, counts = validate(args.root.resolve())
    for name, count in sorted(counts.items()):
        print(f"{name}: {count} skills")
    for error in errors:
        print("ERROR: " + error)
    print(f"Repository validation: {'FAILED' if errors else 'passed'} ({sum(counts.values())} skills; {len(errors)} errors)")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
