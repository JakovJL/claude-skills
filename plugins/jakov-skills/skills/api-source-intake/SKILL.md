---
name: api-source-intake
description: Extract a traceable API contract from OpenAPI, Swagger, Postman or Bruno collections, documentation, curl examples, or route definitions. Use to establish endpoints, authentication, request and response shapes, data dependencies and gaps before documentation or test planning.
---

# API source intake

Produce a source-backed API evidence note for the requested service or workflow. Keep discovered behavior distinct from inference and unresolved questions.

## Establish the source

Read [source routing](references/source-type-routing.md) for the source format in front of you. Prefer structured specifications and collection exports. A Swagger UI may expose its backing specification; do not scrape the interface when that file answers the question.

Use route/controller code to establish what it actually defines, retaining file and line references. Do not infer a conventional endpoint, parameter or response from a resource name. Reconcile conflicting versions rather than quietly combining incompatible contracts.

Inspect relevant local sources, test helpers and configuration examples before asking for missing inputs. Ask only for facts that materially block the scoped extraction and cannot be established from the available evidence.

## Extract

Use the [evidence schema](references/api-evidence-artifact.md), scaling its detail to the requested subset:

1. Identify source location, revision or access time, scope and environment.
2. Record method, path, purpose, authentication mechanism, request and response shape, errors, pagination and limits where documented.
3. Record data dependencies, idempotency and side effects. Classify operations as read-only, mutating, destructive/high-risk or unclear from evidence, rather than from the HTTP method alone.
4. Attach source references to endpoint facts. Mark inferred or unconfirmed fields beside the field.
5. List material gaps and contradictions, including endpoints whose contract could not be resolved.

Describe credential requirements without copying values, cookies or private request data into the artifact.

## Live checks and rendered documentation

Read [live-probe boundaries](references/live-probe-safety.md) before considering a request to the target service. Reuse authorization already supplied for the task; extracting static documentation does not by itself authorize a probe or a load test.

When relevant content requires an interactive browser, use an available browser tool. The sibling [rendered-web-source-extract](../rendered-web-source-extract/SKILL.md) provides an evidence protocol when installed. Missing that skill does not prevent ordinary source extraction with available tools; disclose content you could not reach.

## Deliver

Return the note or save it at the requested destination. For larger follow-up work, explain which confirmed fields support documentation, automation or performance planning using the [handoff guide](references/downstream-use.md). Do not require another skill, create a knowledge base, run tests or update an external tracker unless that work is part of the user's request.
