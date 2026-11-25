# API Evidence Artifact

## Purpose

The single output this skill produces: a portable, traceable Markdown
record of an API's surface as evidence, not a functioning client or a
finished plan - shaped so a downstream skill (knowledge base,
performance-test planning, test-automation planning) or a human can act
on it without re-deriving the facts from the raw source.

## Scope: One Artifact Per Extraction Pass

One artifact covers one API, or one clearly-scoped subset of it (e.g.
one resource's endpoints, one workflow's calls) reached from one source
or one small set of closely related sources (a spec file plus the docs
page that adds prose context to it). A genuinely large API surface can
be split into several artifacts by resource/domain grouping rather than
forced into one unwieldy file - state the scoping decision explicitly
either way.

## Top-Level Metadata

- **Source type** - one of the shapes in `source-type-routing.md`
  (OpenAPI/Swagger, Postman/Bruno collection, static docs page, rendered
  docs UI via `rendered-web-source-extract`, source-code routes, live
  probe).
- **Source location** - file path, URL, or repo path, exact enough to
  re-find it.
- **Access timestamp** - when this extraction happened.
- **Base URL / server information** - if present in the source (an
  OpenAPI `servers` block, a collection's base-URL variable, a docs
  page's stated host). State per-environment values (e.g. staging vs
  production hostnames) if the source distinguishes them; note plainly
  if no base URL is stated anywhere in the source.
- **Extraction goal / scope** - the whole surface, or the specific
  subset this pass covers.

## Per-Endpoint Fields

One entry per endpoint (or per logical group, for a large, uniform set -
state the grouping rule if used):

- **Method + path** - exactly as the source states it, including path
  parameters in their real placeholder form (e.g. a path parameter
  written the way the source itself writes it, not invented).
- **Purpose / summary** - what the endpoint does, from the source's own
  description where one exists; a short factual restatement (not
  editorializing) when the source has no prose but the purpose is
  unambiguous from context (e.g. a structured spec's own path/method
  naming).
- **Auth requirements** - the mechanism (API key header, bearer token,
  OAuth2 flow, session cookie, none) and where it's enforced (per-route,
  per-router, globally) - never an actual credential value (see
  `SKILL.md` Guardrails).
- **Request parameters / body shape** - path/query/header parameters and
  request body schema, with which are required vs optional where the
  source states it. Note the schema's source (formally declared vs
  inferred from a handler/model) - see Confidence Tagging below.
- **Response shape / status codes** - success and error response shapes,
  and every status code the source documents or the handler logic
  implies.
- **Pagination / filtering / sorting** - the mechanism if the endpoint
  supports it (cursor, offset/limit, page tokens; filter/sort query
  parameter conventions) - state "not applicable" or "not documented"
  rather than omitting the field silently.
- **Idempotency / mutation behavior** - whether repeating the same
  request is safe (a `GET` or a properly idempotent `PUT`/`DELETE`) or
  has cumulative/unsafe effects on repeat (a `POST` that creates a new
  resource each call). This is distinct from, and feeds, the safety
  classification below.
- **Safety classification** - exactly one of:
  - `read-only` - no state change, safe to call freely once auth/rate
    limits are respected.
  - `mutating` - changes state in an ordinary, expected, reversible-ish
    way (creates/updates a resource as its normal function).
  - `destructive / high-risk` - deletes data, is irreversible, affects
    more than the caller's own scope, or has a blast radius beyond what
    a single normal call should have.
  - `unclear` - the source doesn't give enough evidence to classify
    confidently; say so rather than defaulting to `read-only` (the
    non-conservative direction) or over-flagging every mutation as
    `destructive` (the direction that makes the classification useless).
- **Data dependencies / test-data requirements** - what has to exist
  first for this endpoint to be callable meaningfully (a valid resource
  ID from a prior create call, a specific account state, a seeded
  record) - relevant to both test-automation and performance-test
  planning downstream.
- **Rate limits / timeouts / retry behavior** - if the source states
  any (a documented requests-per-minute limit, a stated timeout, a
  retry-after header convention) - state "not documented" rather than
  omitting when the source is silent, since that silence is itself
  useful information for performance-test planning.
- **Observability / correlation IDs** - a request/trace/correlation ID
  header or convention, if the source documents one - relevant to
  anyone later trying to trace a call through logs/traces.
- **Open questions / unsupported assumptions** - anything about this
  endpoint that couldn't be confirmed from the source: an ambiguous
  field type, a response shape only partially documented, a safety
  classification made on inference rather than explicit evidence. This
  field is not optional filler - a clean-looking artifact with no open
  questions on a source that was genuinely incomplete is a worse outcome
  than one that honestly says what's missing.

## Confidence Tagging

Tag a field's basis explicitly when it isn't a plain, direct restatement
of the source: `stated` (source says this directly), `inferred`
(reasonably derived from adjacent evidence - a handler's model class, a
naming convention strongly implied by the rest of the spec), or
`unconfirmed` (a real gap, recorded as an open question rather than a
best guess). Carry this tag through to any downstream use rather than
letting an `inferred` or `unconfirmed` field read as if it were
`stated`.

## Skeleton Example

Placeholder values only - never a real project's endpoints, payloads,
base URLs, or credentials in this skill's own files.

```markdown
# API Source Evidence: <short description of the API/subset>

**Source type:** OpenAPI file
**Source location:** <path or URL>
**Access timestamp:** 2026-01-01T12:00:00Z
**Base URL / server info:** https://api.example.com/v1 (production);
https://staging-api.example.com/v1 (staging, stated separately in source)
**Extraction goal / scope:** <the API surface or subset this covers>

## Endpoint: GET /widgets/{widget_id}

- **Purpose:** Retrieve a single widget by ID. (stated)
- **Auth:** API key via `X-Api-Key` header, enforced globally. (stated)
- **Request:** Path parameter `widget_id` (string, required). (stated)
- **Response:** `200` with widget object `{id, name, status, created_at}`;
  `404` if not found. (stated)
- **Pagination/filtering/sorting:** Not applicable (single-resource GET).
- **Idempotency/mutation:** Read-only, safe to repeat.
- **Safety classification:** `read-only`
- **Data dependencies:** Requires an existing widget ID. (stated)
- **Rate limits/timeouts/retry:** Not documented in this source.
- **Observability:** `X-Request-Id` echoed in response headers. (stated)
- **Open questions:** Response schema for `status` field's possible
  enum values isn't listed anywhere in the source. (unconfirmed)

(Repeat one entry per endpoint or logical group.)
```
