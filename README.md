# claude-skills

Personal [Claude Code](https://code.claude.com) skills, packaged as a plugin marketplace so they install with one command.

| Skill | What it does |
|---|---|
| `load-test-report-writing` | Turns load-, stress- or performance-test results (Gatling, JMeter, k6, Locust, ...) into a short report of at most two pages plus a full technical report: a verdict per run, per-user wait times instead of averages, persistence and server checks, interference on the test environment, like-for-like comparisons. Publishes them as clean Google Docs and checks every page visually. |

## Install

As a plugin (recommended). In Claude Code:

```
/plugin marketplace add JakovJL/claude-skills
/plugin install jakov-skills@jakov-claude-skills
```

or from a shell:

```
claude plugin marketplace add JakovJL/claude-skills
claude plugin install jakov-skills@jakov-claude-skills
```

Plugin skills are namespaced: `/jakov-skills:load-test-report-writing`. Claude also picks the skill up on its own when a request matches.

Update later with `/plugin marketplace update jakov-claude-skills`.

Manual install instead: copy the folders from `plugins/jakov-skills/skills/` into `~/.claude/skills/` (all your projects) or into a project's `.claude/skills/`. Do not install both ways at once, or the same skill appears twice.

## Requirements

| Skill | Needs |
|---|---|
| `load-test-report-writing` | Python 3 for `md2gdoc.py`; the `google-workspace` MCP server to publish Google Docs; Windows PowerShell 5.1 for `pdf2png.ps1` (renders exported PDFs with the built-in Windows PDF API). The writing method itself works anywhere. |

## Usage examples

- "Write the report for today's three Gatling runs, short and full, as Google Docs in English."
- "Is the 500-in-30-s run worse than last week's? Compare them properly."
- "Why does the p95 look almost the same as the max here? Is the report wrong?"

## What the skill insists on

- The first paragraph answers the question (did the system hold the planned users, and how long did people wait), with numbers.
- Waits are reported per user, not only per request, with median, p95, maximum and the share of users over 3 / 10 / 15 s. No averages.
- Every number comes from the run artifacts or a check that was actually run; unknowns are written as unknown.
- Functional bugs and personal data (names, emails, tokens) stay out of the report.

## Layout

```
.claude-plugin/marketplace.json        marketplace "jakov-claude-skills"
plugins/jakov-skills/
  .claude-plugin/plugin.json           plugin "jakov-skills"
  skills/<skill>/SKILL.md              one folder per skill, with scripts/ and references/
```

Skills find their own files through `${CLAUDE_SKILL_DIR}`, so the same folders work as a plugin and as manually installed skills.

## License

[MIT](LICENSE)
