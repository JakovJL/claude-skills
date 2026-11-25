# claude-skills

Reusable [Claude Code](https://code.claude.com/docs/en/skills) skills packaged as a plugin covering QA, evidence intake, performance work, media and engineering verification.

## Install

In Claude Code:

```text
/plugin marketplace add JakovJL/claude-skills
/plugin install jakov-skills@jakov-claude-skills
```

The same commands work from a shell with `claude plugin` instead of `/plugin`. Update the marketplace with `/plugin marketplace update jakov-claude-skills`.

Invoke a skill as `/jakov-skills:aqa-playbook`. Claude can also select a relevant skill automatically. Manual installation is supported: copy complete skill folders from `plugins/jakov-skills/skills/` into `~/.claude/skills/` or a project's `.claude/skills/`. Do not install the same skill both ways.

## Core skills

| Skill | Purpose |
|---|---|
| [api-source-intake](plugins/jakov-skills/skills/api-source-intake/SKILL.md) | Extract an API contract from specifications, collections, documentation or route definitions, with source references and explicit gaps. |
| [aqa-playbook](plugins/jakov-skills/skills/aqa-playbook/SKILL.md) | Plan proportionate QA coverage, investigate UI/API behavior, reproduce defects and record raw evidence. |
| [performance-scenario-design](plugins/jakov-skills/skills/performance-scenario-design/SKILL.md) | Design a grounded workload, data strategy, criteria and observability before implementing or running load scripts. |
| [load-test-report-writing](plugins/jakov-skills/skills/load-test-report-writing/SKILL.md) | Write short and full load-test reports with per-user waits, persistence checks, comparable runs and optional Google Docs publishing. |
| [meeting-transcript-extract](plugins/jakov-skills/skills/meeting-transcript-extract/SKILL.md) | Extract attributed facts, decisions, actions and uncertainties using meeting categories or a caller-provided taxonomy. |
| [rendered-web-source-extract](plugins/jakov-skills/skills/rendered-web-source-extract/SKILL.md) | Capture traceable evidence from interactive web pages when structured access is insufficient. |
| [video-trim-and-audio-extract](plugins/jakov-skills/skills/video-trim-and-audio-extract/SKILL.md) | Detect a recording's idle tail, cut or extract audio, and optionally transcribe through an explicitly selected external service. |
| [windows-release-verification](plugins/jakov-skills/skills/windows-release-verification/SKILL.md) | Verify revision, package, exact installer, normal shortcut launch and artifact identity. |
| [llm-trace-replay](plugins/jakov-skills/skills/llm-trace-replay/SKILL.md) | Freeze and reconstruct LLM requests; validate fixture hashes offline before application-owned or authorized live comparisons. |
| [safe-config-migrations](plugins/jakov-skills/skills/safe-config-migrations/SKILL.md) | Preview configuration changes, detect stale plans and recover/restore owned changes without overwriting later edits. |
| [requirements-traceability](plugins/jakov-skills/skills/requirements-traceability/SKILL.md) | Maintain requirement/criterion/test links and validate a portable registry without claiming tests were executed. |
| [realtime-latency-diagnosis](plugins/jakov-skills/skills/realtime-latency-diagnosis/SKILL.md) | Separate service time, queue growth, shutdown tails and visible latency in live pipelines. |
| [publication-anonymization](plugins/jakov-skills/skills/publication-anonymization/SKILL.md) | Sanitize technical material while retaining measurements, evidence limitations and source notices. |
| [windows-support-diagnostics](plugins/jakov-skills/skills/windows-support-diagnostics/SKILL.md) | Investigate Windows failures, plan scoped repairs and verify the original symptom in the affected environment. |
| [codex-delegate](plugins/jakov-skills/skills/codex-delegate/SKILL.md) | Coordinate an authorized local Codex CLI worker and independently review the result. |
| [opencode-delegate](plugins/jakov-skills/skills/opencode-delegate/SKILL.md) | Coordinate a permitted OpenCode worker with explicit scope, account/model selection and verification. |

These are reusable methods. Project endpoints, credentials, registries, recorded cases and acceptance thresholds remain with the project. Installing a skill does not start a load test, call a provider, edit configuration or publish a repository.

## Optional dependencies

Instructions can be read without installing a runtime. Dependencies apply only to the operation being used:

| Operation | Needs |
|---|---|
| Offline replay integrity and traceability helpers | Python 3.10+; standard library only. |
| Recording analysis/cutting/audio extraction | Python and `ffmpeg`/`ffprobe` on PATH. |
| Optional external transcription | Explicitly authorized audio upload and an ElevenLabs API credential. No credential is bundled. |
| Optional local speaker comparison | The media reference documents its separate local model and Python dependencies. No voice profiles, recordings or model weights are distributed. |
| Google Docs report publishing | Python, an available Google Workspace MCP connection, and an export/render path; the bundled PDF renderer uses Windows PowerShell 5.1. |
| CLI delegation | A separately installed and signed-in Codex or OpenCode CLI, an available selected model, and authorization under the current project workflow. |

## Local development checks

Repository validation uses Python 3.10+ and PyYAML. It checks the marketplace and plugin manifest, all skill entrypoints, excluded candidate skills, local resource links, private-machine markers and Python syntax:

```sh
python tools/validate_repository.py
python -m unittest discover -s tests -v
git diff --check
```

Use `claude plugin validate .` and `claude plugin validate plugins/jakov-skills` when a compatible Claude CLI is available. Validation and fixture checks do not establish actual media encoding, provider behavior or target-machine acceptance.

## Layout and license

```text
.claude-plugin/marketplace.json
plugins/jakov-skills/.claude-plugin/plugin.json
plugins/jakov-skills/skills/<skill>/SKILL.md
tools/validate_repository.py
```

Skill commands resolve their resources through `${CLAUDE_SKILL_DIR}`. Runtime references stay inside their plugin. See [MIT](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md) for source attribution and retained notices. External applications, services, optional models and libraries retain their own terms.
