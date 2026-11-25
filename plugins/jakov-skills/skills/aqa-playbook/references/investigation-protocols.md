# Investigation protocols

Select protocols that can answer the current defect question. Keep a record of the triggering condition, control, raw evidence and cleanup.

## Forms and negative input

Establish the accepted contract before varying missing, empty, malformed, boundary or conflicting values. Inspect validation, focus/error state, submission and persisted data. A browser block and a server response test different layers. A 5xx on malformed input is a candidate defect whose expected behavior and environment still need establishing.

## Data propagation and caching

Follow the write from its actual entry point to storage, API, UI and another session when relevant. Compare timestamps, cache state, identities, locale/currency and documented consistency window. An immediate old value is not a defect merely because the system has a documented eventual-consistency contract.

When UI and API disagree, establish that they refer to the same variant, region, taxes, permissions and data version before declaring a mismatch. Use requirements to decide which value is correct.

## Intermittent behavior

Preserve the first observation and relevant timing, session and state. Repeat only enough to narrow a useful hypothesis within the requested budget. Record attempts and outcomes rather than declaring a universal reliability rate from a small sample.

Change one condition where feasible: cold versus warm state, fresh versus existing session, slow network, repeated action or competing request. If the symptom no longer appears, report it as not reproduced under those conditions; do not erase the initial evidence.

## Races and idempotency

Use authorized disposable data. Compare an ordinary operation with double-submit, retry, concurrent update or replay only where that behavior is meaningful to the contract. Inspect final records, counts and ownership; response status alone does not establish one durable effect.

Some operations intentionally allow repeats. Establish the intended idempotency key, retry semantics and state transitions before calling duplicates a bug. Avoid recreating a money-loss or destructive incident just to reach a reproduction count.

## Symptom inventory and cause

Trace from user trigger through the relevant calls to the failure. Ask whether the proposed code change runs on that path. Inspect related paths affected by a supported shared cause; keep distinct causes separate even when the user-visible message is similar.

For third-party behavior, distinguish the upstream contract/limitation, the integrating product's handling and environment failures. Record which layer the evidence actually supports.

## Evidence and status

- Observed: a raw observation exists.
- Candidate: the observation could be a defect; expected behavior or reproducibility remains unresolved.
- Reproduced: a documented path recreates it under stated conditions.
- Confirmed: available evidence establishes the contract violation and rules out the material alternatives.

Use project status names when provided. State the grounds for confidence; these labels do not require fixed attempt counts or every kind of artifact.
