---
name: codex-delegate
description: Delegate a bounded read-only investigation or authorized implementation task to a separately installed local Codex CLI, then independently review its evidence and changes. Use when that additional worker is requested or permitted by the current project workflow.
---

# Delegate a bounded task to Codex CLI

Read the current project instructions and Git state. Confirm that delegation is allowed, the CLI is installed and its account/model is available. This skill is a coordination method; installing it does not authorize paid runs, account changes or sending private material to another provider.

Define one useful independent result: goal, directory, allowed files, read-only/edit scope, minimum necessary context, expected evidence and checks. Keep credentials and unrelated private content out of the prompt. The worker must not commit, push, change branches, publish, install software or expand scope unless that exact action is authorized.

## Invoke the installed CLI

Inspect `codex exec --help` for the current flags. Select the user's requested model when available; otherwise use a suitable model already configured for that CLI. Do not hardcode a subscription or universal model default, or silently switch provider/account on failure.

For a read-only task, the usual invocation is:

```sh
codex exec --cd ./project --sandbox read-only --ephemeral "Inspect the named files and return the requested evidence."
```

Add `--model` only after resolving the intended available model. For authorized editing use the CLI's supported workspace-write mode and give an explicit file scope. On Windows, avoid command strings that interpolate multiline prompts through multiple shells; use the CLI's documented stdin/file input when available. Shell escaping is not permission control.

Do useful independent work while the same worker runs. A short progress poll is not a timeout and not a reason to terminate it. Use a task-appropriate budget, preserve failure output and report CLI/auth/model failures separately from investigation findings.

## Review before integration

Treat the final answer as claims to verify. Inspect changed paths and diff, preserve unrelated edits, check cited source locations and run the task's relevant checks. An empty/truncated answer or unavailable review is not a passed check. Respect repository restrictions on concurrent writers and extra worktrees.

Return what the worker did, what you independently verified, actual check results and remaining gaps. The coordinating agent retains responsibility for the user-facing outcome and any authorized external action.
