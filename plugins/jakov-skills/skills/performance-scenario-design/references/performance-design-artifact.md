# Performance design artifact

Use these fields where they affect the decision. A small baseline may fit in a compact table; related profiles can share one comparison document.

## Context

- Decision and measurable user-facing objective.
- Sources and revision/time; target environment and deployed build.
- Scope: roles, workflow, endpoints and excluded work.
- Material differences from a previous baseline.

## Scenario table

| Order | Scenario | Participants or rate | Ramp and duration | Think time | Targeted action window | Purpose | Transition or stop condition |
|---|---|---|---|---|---|---|---|
| 1 | Comparable baseline | Evidence-backed value or labeled proposal | Explicit window | Explicit pauses | State whether synchronized | Establish baseline | Defined correctness and health checks |

Populate values from evidence or mark them as proposed/unknown. Do not leave a guessed number looking agreed. State the arrival model and whether concurrency is a target, a derived effect or a measured result.

## Data and expected outcomes

- Fixture creation/reuse, identities, authentication/session lifecycle and limits.
- Expected per-participant records and business state transitions.
- Persistence verification, duplicate/cross-user checks and cleanup or retention.

## Evaluation

- Team criteria or clearly labeled working thresholds.
- User-facing step timing and completion, endpoint errors and retries, dropped arrivals and timeouts.
- Generator, application, database and downstream health where available.
- Clock/timezone, observation windows and correlation identifiers.
- Stop, recovery and escalation conditions; unresolved dependencies that prevent a meaningful run.

## Handoff

List confirmed inputs, proposals and open decisions beside the profiles they affect. State the intended report format and artifact locations when established by the project. Implementation follows the project's engine conventions; a design is not a run result or execution approval.
