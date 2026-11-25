# Browser Extraction Workflow

Load this file once the API-vs-browser precheck has concluded browser
extraction is the right path for this source.

## Deliberate Navigation

State the extraction goal (see `SKILL.md`, Required Start step 2) before
opening the browser, then plan the minimum sequence of interactions
likely needed to reach it - which tab, which accordion, roughly how many
pagination pages, which modal. This is a plan to work from, not a rigid
script; adjust as the real page reveals itself, but avoid open-ended
exploration with no goal in view.

## Interaction Logging

Log every interaction as it happens, in order - a navigation, a tab
switch, an accordion open, a "load more" click, a pagination advance, a
modal open/close. This log becomes the evidence artifact's visited-states
field (see `references/source-evidence-artifact.md`) - it's what lets a
downstream reader (human or another skill) understand exactly what was
checked and what wasn't, without re-running the extraction themselves.

## Targeted Extraction

Prefer a scoped read over a full-page dump whenever the extraction goal
only needs part of the page:

- Scope a snapshot/evaluate call to the specific region/selector holding
  the needed content rather than dumping the entire accessibility tree or
  DOM.
- When the page exposes a structured read internally (a table, a list,
  a rendered API response visible in a network/devtools panel), prefer
  extracting that structure directly over flattening it to prose - a
  table's rows/columns, a list's items, and real link `href`s carry
  meaning a flattened text scrape loses.
- Capture structural context alongside the prose: headings (and their
  level), list/table shape, real link targets next to their anchor text,
  and any explicit metadata visible on the page (author, last-updated
  date, version label).
- A broad, unscoped dump is acceptable only when the extraction goal
  itself is genuinely broad ("what's on this page overall") and a
  targeted read would leave real gaps - state that reasoning rather than
  defaulting to it.

## Paginated / Lazy-Loaded / "Load More" Content

Don't assume the first screen is complete. For content behind pagination,
infinite scroll, or a "load more" control:

- Check for and exhaust the relevant control(s) when the extraction goal
  needs the full set (e.g. "every item in this list").
- If exhausting them isn't feasible (an unbounded/very large list, a
  control that doesn't reach a clear end), stop at a reasonable point and
  record exactly what was and wasn't covered in the artifact's gaps/
  uncertainties field - never present a partial read as if it were
  complete.

## Screenshot Judgment

Capture a screenshot only when the rendered/visual state is itself
material to the extraction goal - a UI's actual appearance, a layout, a
live dashboard reading at a specific point in time. When captured, record
why it's evidence (what it shows that text extraction alone wouldn't) in
the artifact's extraction notes. Do not use a screenshot as a default or
convenient substitute for reading text directly - it isn't searchable,
isn't structured, and doesn't belong in the artifact just because it was
easy to take.

## Credential And Secret Hygiene

Never capture, log, or re-transcribe cookies, authorization headers,
session tokens, or the contents of a credential/storage panel, even if
they become visible incidentally while inspecting network traffic or
devtools for another reason. If a captured region happens to include such
data, redact it before it goes anywhere near the evidence artifact -
never carry it through "for completeness."

## Stop Conditions

State a rough action budget before starting (a small number of
navigation/click/eval actions, sized to the extraction goal's real
complexity). If the goal isn't reached within that budget:

- Stop rather than continuing open-ended exploration.
- Report what was found, what wasn't, and why (a control that didn't
  behave as expected, content that never appeared, a navigation path that
  didn't converge).

If the browser tool itself becomes unreliable (repeated crashes, hangs,
navigation failures), don't keep retrying blindly - report the failure
and whatever was captured before it, per `api-vs-browser-precheck.md`'s
missing-capability guidance.
