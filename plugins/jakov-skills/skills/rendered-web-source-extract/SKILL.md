---
name: rendered-web-source-extract
description: Extract traceable evidence from pages whose relevant content requires rendering or interaction, including tabs, pagination, accordions and dashboards. Use when a structured API or static fetch cannot supply the requested content; record visited states, source time and coverage gaps.
---

# Extract evidence from a rendered page

Capture the content and state that answer the user's question, with enough provenance to distinguish a partial view from complete coverage.

## Choose the access path

Read the [API versus browser precheck](references/api-vs-browser-precheck.md). Prefer an available connector, structured API or static document when it provides the required information. Browser interaction is useful when the content or visual state actually depends on rendering, not merely because a tab is open.

Use the browser tool available in the current environment; this skill does not require a particular driver. When no renderer is available, return any useful static evidence with its limits and identify the content that remains inaccessible. Do not claim the static result represents an unvisited interactive state.

## Extract

Follow the applicable parts of [the interaction workflow](references/browser-extraction-workflow.md):

1. Establish the extraction goal, relevant sections and a proportional action budget.
2. Navigate toward that goal, recording material state changes such as selected tabs, filters and pagination.
3. Extract targeted headings, tables, text and actual link targets. Preserve the source's structure where it carries meaning.
4. Exhaust relevant pagination or explicitly state what remains unread. Distinguish a filtered result from the whole source.
5. Capture screenshots when appearance, layout or a displayed measurement is evidence. Text extraction does not automatically need screenshots.
6. Record uncertainty, inaccessible states and any truncation. Stop an unproductive navigation loop and report the remaining gap.

Do not export cookies, authentication headers, browser storage or unrelated account details. Keep captured evidence within the authorized destination and audience.

## Deliver

Use the [evidence artifact](references/source-evidence-artifact.md): URLs, access time, rendered titles, extraction goal, visited states, extracted content and coverage gaps. Return it or save it where requested. Summarize or incorporate it into another document when the user requested that work; the extraction itself does not authorize external publication or messages.
