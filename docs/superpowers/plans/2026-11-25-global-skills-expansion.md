# Global Skills Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Package the approved reusable workflows in the existing marketplace, excluding all three candidate-legend skills.

**Architecture:** Keep the existing reporting skill and add general engineering, evidence intake, QA, media and diagnostic skills to `plugins/jakov-skills/skills/`. Every plugin must contain its own referenced resources.

**Tech Stack:** Agent Skills Markdown/YAML, Claude Code JSON manifests, Python 3 standard-library helpers; existing optional media dependencies.

## Global Constraints

- Exclude `candidate-legend`, `candidate-legend-description` and `candidate-legend-questions`.
- Project URLs, credentials, private transcripts, voice profiles, personal paths and historical measurements are not distribution assets.
- Preserve the original reporting skill unless a concrete validation defect requires a narrow fix.
- Skill instructions do not authorize provider calls, live load tests, configuration writes, publication or external messages beyond the user's task.
- Do not run OpenCode or other provider-backed worker CLIs for validation. Use local fixtures and available independent reviewers.
- Local source projects and installed skills remain read-only. Workers edit only their assigned new plugin folders; no worker commits or pushes.
- Use `${CLAUDE_SKILL_DIR}` for commands in skill instructions.

## Task 1: Package evidence, QA and media skills

**Files:** Six new directories in `plugins/jakov-skills/skills/`: `api-source-intake`, `performance-scenario-design`, `meeting-transcript-extract`, `rendered-web-source-extract`, `aqa-playbook`, `video-trim-and-audio-extract`.

**Sources:** The first four and media skill come from the local performance kit's `.agents/skills/`; QA comes from `AI-QA-sandbox-test/.opencode/skills/aqa-playbook/`.

- [x] Copy supporting references and scripts; omit host-specific `agents/openai.yaml` metadata and generated files.
- [x] Shorten descriptions, remove unavailable downstream skill requirements, preserve useful source attribution, and parameterize script invocation paths.
- [x] Keep QA investigation proportional to the requested surface; provide reproducibility and counterchecks without mandatory run counts or automatic issue publication.
- [x] Validate YAML and local links; run each included script's `--help`. Media operations use generated fixtures only; no transcription upload or voice-library enrollment.

## Task 2: Add reusable engineering workflows

**Files:** New `SKILL.md` files for `windows-release-verification`, `llm-trace-replay`, `safe-config-migrations`, `requirements-traceability`, `realtime-latency-diagnosis`, `publication-anonymization`, `windows-support-diagnostics`, `codex-delegate`, and `opencode-delegate`.

- [x] Author concise, project-independent workflows from the audited source procedures. Link focused references only where useful.
- [x] Add a configurable requirements checker for a JSON registry of requirements, acceptance criteria and test references. Reject duplicate IDs, unknown references and paths escaping the selected project.
- [x] Add an offline LLM replay-manifest validator: verify exact message JSON hashes and optional knowledge-file hashes; keep provider execution in the application-owned adapter.
- [x] Update delegation instructions to respect project authorization and current CLI capabilities; do not hardcode a paid subscription, provider or model as a universal default.
- [x] Exercise the two new scripts on valid, inconsistent, escaped-path and tampered-hash fixtures.

## Task 3: Integrate marketplace and discovery

**Files:** `.claude-plugin/marketplace.json`, the plugin manifest, `README.md`, `THIRD_PARTY_NOTICES.md`, `tools/validate_repository.py`.

- [x] Keep one `jakov-skills` plugin with an explicit version and the approved workflow catalog.
- [x] Document installation, the skill catalog, dependencies, boundaries and local validation command.
- [x] Make the repository validator check manifests, frontmatter, unique names, required resources, Python syntax and excluded candidate skills.
- [x] Keep runtime resources self-contained inside each plugin and reject broken cross-plugin resource links.

## Task 4: Independent verification and delivery

- [x] Run `python tools/validate_repository.py` and the bundled `skill-creator/scripts/quick_validate.py` for every skill folder.
- [x] Run behavioral checks with temporary synthetic fixtures and review the actual files and outputs.
- [x] Give independent reviewers realistic tasks for selected workflows without an expected answer; fix material findings.
- [x] Run `git diff --check`, inspect changed paths, and verify that the candidate-legend family is absent.
- [x] Report exact skill/plugin counts, verification results and runtime checks that require unavailable tools. Prepare the complete local result before any publication approval.
