# Risk-based domain checks

Use applicable items as investigation prompts, not a mandatory full-suite expansion.

## Shared web and API risks

- Empty, loading, error and recovery states on the requested path.
- Authentication/session transitions and role/object isolation.
- Types, validation, pagination/count, filters, sorting and documented errors.
- Keyboard, labels, focus and screen-reader semantics on affected controls.
- Relevant security headers and cookie/session behavior; report observations without declaring legal compliance.
- Cold/warm behavior, resource or payload growth and deterministic cleanup.

## Commerce

Compare the same variant, region, currency, taxes and promotion. Check quantity boundaries, cart/session transfer, stock contention, shipping selection, checkout final state and duplicate effects when those paths are in scope. Never perform a real purchase merely for a bug hunt.

## Billing and multi-tenant systems

Inspect tenant/object ownership, quota boundaries, lifecycle transitions, webhook retries and idempotency. Use test billing or synthetic state; a visual paid callback alone is not proof of a server-authorized payment.

## Content and files

Inspect accepted type/size, interrupted upload, conversion failure, URL lifecycle and cache consistency. Preserve the original source and verify that a failed conversion does not appear successful.

## Real-time systems

Check ordering, duplicates, reconnect, stale state after session change, late events after cancellation and interactions between stream events and ordinary requests. Compare recorded event order with what the user actually sees.
