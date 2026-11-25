# Live-probe boundaries

Use this reference when static sources leave a material contract question and a request to the service may resolve it.

## Before a request

1. Read the task's existing authorization and project restrictions. Reuse permission that already covers the exact target and operation; ask only for a materially new boundary.
2. Identify the service and environment. Do not assume an endpoint is disposable because its URL contains a test-like word.
3. Determine side effects from source evidence. GET is not proof of read-only behavior, and an unknown operation stays unclear until resolved.
4. Verify the request shape, test inputs, authentication mechanism and expected response. Do not send guessed payloads merely to discover what a write endpoint does.
5. Bound requests, timeout and retries to the unresolved question. Respect rate limits, failures and backoff.

## Execute and record

Prefer the smallest authorized read-only request. Writes require scope that actually covers them and a data isolation or cleanup plan. A documentation task alone does not supply that authorization.

Record method, redacted target, safe request shape, environment/build, time, status and the relevant response evidence. Remove credential values and unrelated personal data. Keep an observed response separate from a guarantee about all valid inputs or future deployments.

A blocked request is evidence of a check that did not complete, not proof that the endpoint is absent or broken. Return the useful static contract with the remaining gap when live access is unavailable or prohibited.
