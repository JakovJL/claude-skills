# Data and environment strategy

## Environment

Name the target, purpose, owner/window when relevant, deployed build and shared dependencies. A planning artifact can contain an unresolved environment; it must explain which execution decisions depend on that answer. Local implementation and target execution are separate actions.

Honor the task's existing authorization and restrictions. Neither a production label nor a test label supplies permission by itself. Resolve an unknown target before executing against it. Do not create repeated approval gates for an already authorized environment and workload.

## Classify the steps

- **Read-only:** establish whether the request has hidden writes, background work, expensive downstream calls or growing data.
- **Mutating:** define owned fixtures, identities, unique correlation IDs and the expected persisted results.
- **Destructive/high-risk:** isolate data and dependencies; state recovery feasibility and any boundary that exceeds the current task.
- **Unclear:** preserve the uncertainty and identify the smallest source check or authorized probe that resolves it.

## Data and authentication

State dataset size, creation/reuse rules, uniqueness, exhaustion behavior and how one user's results remain isolated. Include source state or reset strategy so later runs are comparable. Test-generated growth can change payload sizes and server work even if participant counts stay constant.

Describe authentication and session lifecycle, token refresh and the number of usable identities without recording secret values. Consider contention caused by shared accounts and whether it reflects actual use.

## Pacing and synchronization

Justify registration time, reading/answering time and pauses from user behavior or an explicit stress objective. A synthetic synchronized submit is valid when labeled as that question. Specify the planned and measured release window rather than assuming all users act together.

## Cleanup and persistence

For writes, define disposable data, a feasible cleanup method or intentional retention and its consequences. Cleanup must remain within authorization. Reconcile expected and actual records by participant/correlation ID, detect duplicates and cross-user data, and distinguish HTTP success from durable persistence. A timed-out client may still have produced a saved result.
