---
name: opencode-delegate
description: Delegate a cohesive, well-specified implementation or read-only review to an available OpenCode CLI when the user or project permits it. Keep scope, model/account selection, worker permissions and independent verification explicit.
---

# Delegate settled work to OpenCode

Use for a package with a stable interface and acceptance criteria: a focused helper, translations with final source strings, documentation based on verified behavior, or a bounded diff review. Keep unresolved architecture, root-cause diagnosis, final integration and real-interface acceptance with the lead agent. Handle tiny coupled edits directly.

Check current project instructions before starting. A project may prohibit unsolicited delegation or require a particular provider. Do not infer an active subscription from old memories. Installing this skill does not authorize a provider run.

## Prepare the worker task

Inspect relevant files and `git status`. Give the worker:

- a concrete objective and approved inputs;
- the working directory and exact allowed files;
- constraints, including preservation of existing dirty work;
- observable acceptance criteria and the targeted checks;
- a request to report changed files, checks/results, preserved behavior and unresolved risks.

Do not send credentials, recordings, private transcripts or unrelated user content. Keep a read-only review explicitly read-only. The worker must not commit, push, branch, publish, modify unrelated files or install dependencies under an implementation-only request.

## Run without assuming local defaults

Check the installed `opencode run --help` and configured model catalog. Resolve the account/provider/model from the user's instruction and current project configuration. Do not silently fall back to another paid model. Use native argument passing or documented file/stdin input for multiline tasks; do not concatenate untrusted text into shell commands.

Use a task-appropriate timeout; the original long-running worker workflow used 50 minutes as a configurable budget, not a service guarantee. A brief empty progress poll does not mean the worker is stuck. Keep the same process running while doing independent work; avoid overlapping writers in a shared checkout.

No auto-approval flag is prescribed here. Choose the tool's actual permission mode to match the task; prompt wording alone cannot confine a fully privileged worker. If a local runner broadens permissions or mutates the user's global configuration, inspect and adapt it before use rather than copying that behavior blindly.

## Verify the result

Read the final message, check changed paths and actual diff, then independently execute the agreed acceptance checks. Examine findings from a reviewer instead of accepting them because another model said so. An empty answer, truncated response, timeout, provider failure or unfinished tool-call stream is a failed/unavailable worker result, never a successful review.

Fix concrete defects within scope; retry only when there is a specific useful correction. Report the work, independent verification, actual usage/cost when available, and remaining gaps. External publication follows the current task's authorization, not the worker's suggestion.
