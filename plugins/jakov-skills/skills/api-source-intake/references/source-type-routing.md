# Route by API source type

## OpenAPI or Swagger

Prefer the structured document over a generated UI. Record its version or hash, server declarations, paths, operations, parameter locations, request content types, response schemas and security requirements. Follow local references and identify unresolved external references. Preserve operation-level overrides rather than applying global authentication blindly.

A document describes the stated contract. Check whether its revision matches the target build when that distinction matters.

## Postman or Bruno collections

Record the collection/export version and relevant environment variable names without their secret values. Resolve base paths and inherited authentication as far as available inputs permit. Examples and tests are evidence of intended use, not a complete response schema; label that limitation.

## Documentation pages and curl examples

Capture the source URL and access time. Separate normative descriptions from illustrative examples. A curl example establishes its shown method, headers and shape, not every accepted field or error.

For an interactive docs page, first look for its backing specification. If relevant material still needs rendering, use an available browser and record the reached states. The sibling rendered-web-source-extract skill can guide that step but is not a prerequisite.

## Route and controller source

Trace router mounts, base prefixes, middleware, serializers and validation to the scope needed for the contract. Attach file/line references. A handler name alone does not establish its public URL, authentication, persistence or response shape. Differentiate statically defined behavior from code paths whose configuration is unknown.

## Live request

Read [live-probe boundaries](live-probe-safety.md) before a request. A sampled response can confirm that case on that environment at that time; do not turn it into an exhaustive contract.
