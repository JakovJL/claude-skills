---
name: requirements-traceability
description: Maintain links between product requirements, acceptance criteria, manual scenarios and automated tests, and detect broken or missing coverage links. Use when adding a critical flow, reviewing acceptance coverage, or keeping requirement IDs and test documentation consistent with implementation.
---

# Keep requirements and evidence connected

Reuse the project's canonical register and ID conventions. Write requirements as user/system behavior, acceptance criteria as observable outcomes and tests/scenarios as ways to verify those outcomes. Keep IDs stable when wording changes; do not reuse an old ID for a different behavior.

For a changed flow, follow its links in both directions. Confirm that the referenced test actually exercises the intended entry point and failure path. A file with a matching name is a traceability link, not proof of behavioral coverage or a passing execution.

## Check a portable registry

When the project has its own checker, use it. Otherwise the bundled standard-library checker accepts this JSON shape:

```json
{
  "requirements": [{"id": "R-01", "criteria": ["AC-01"]}],
  "acceptance_criteria": [{"id": "AC-01", "tests": ["T-01"]}],
  "tests": [{"id": "T-01", "kind": "manual", "path": "docs/scenarios.md"}]
}
```

```sh
python "${CLAUDE_SKILL_DIR}/scripts/check_traceability.py" registry.json --root ./project
```

Use unique IDs across the registry. All three collections are required arrays. Each requirement needs at least one criterion; each criterion needs at least one test/scenario. A test's `kind` is `automated`, `manual` or `planned`. Automated/manual entries name an existing regular file beneath `--root`; planned entries may omit `path`. Unknown references, duplicate IDs, missing files and escaped paths fail validation. Unreferenced tests are reported as warnings. Additional descriptive fields are preserved by the source registry and ignored by the checker.

The output reports link integrity and counts by kind. It never runs tests. A planned entry records intent; a manual scenario is not automated coverage. Record execution evidence and results separately using the project's actual test runner or manual report.

## Make scoped updates

Update the requirement, affected criteria, tests and technical contract together when behavior changes. Keep unrelated material intact. Split long registers by complete topics if needed while preserving a stable index and links. For Markdown or another registry format, adapt an explicit extraction layer rather than scraping arbitrary tables and calling missing rows covered.

Return the affected IDs, resolved/broken links, coverage gaps and actual execution evidence. Where the expected behavior is unconfirmed, mark that gap instead of inventing a requirement to make an existing implementation pass.
