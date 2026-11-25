# Source Evidence Artifact

## Purpose

The single output this skill produces: a portable, traceable Markdown
record of what was extracted from a rendered page, how it was reached,
and what's uncertain about it - shaped so a downstream skill (or a human)
can act on it without re-running the extraction.

## Scope: One Artifact Per Extraction Pass

One artifact covers one page, or a small set of closely related pages
reached in the same navigation session under one stated extraction goal
(e.g. a page and a child page it linked to, both needed to answer the
same question). Don't fragment closely related evidence into several
tiny files, and don't let one artifact silently grow to cover an
unrelated second goal - a new goal starts a new artifact.

## Required Fields

- **Source URL(s)** - exact, including any anchor/fragment actually
  reached (not just the starting URL if navigation moved to a different
  address).
- **Access timestamp** - when the extraction happened, not any
  "last updated" date the page itself displays (record that separately,
  as page metadata, if visible).
- **Page title(s)** - as rendered, for each page covered.
- **Extraction goal** - the question this pass was meant to answer,
  carried from `SKILL.md`'s Required Start step 2. A downstream reader
  needs this to judge whether the artifact actually answers what they
  need.
- **Visited states / interactions** - the ordered log from
  `browser-extraction-workflow.md`'s Interaction Logging: every
  navigation, tab switch, accordion open, pagination advance, "load
  more" click, modal open/close.
- **Extracted content** - the actual text/data, structured where the
  source had structure (headings, lists, tables, real link targets
  alongside anchor text) rather than flattened into one undifferentiated
  block.
- **Screenshots** - only when the rendered/visual state was itself
  material (see `browser-extraction-workflow.md`, Screenshot Judgment);
  each entry names why it's evidence, not just that it exists. Omit this
  field entirely when no screenshot was material - don't include an
  empty placeholder.
- **Extraction notes** - what was skipped, truncated, or simplified, and
  why; any judgment calls made about scope during extraction.
- **Gaps / uncertainties** - content not reached, pagination not
  exhausted, ambiguous or unclear rendering, anything the extraction
  could not confirm. State these explicitly rather than letting a partial
  read pass as complete.
- **Recommended downstream handling** - a *shape*, not a guessed skill
  name unless one is actually confirmed available in the current
  environment: narrative/conversation-shaped (suits a transcript-
  extraction step), cumulative topic-fact-shaped (suits a knowledge-base
  step), or "unclear, ask" if neither fits cleanly.

## What This Skill Does Not Decide

Where the artifact ends up (a file path, a knowledge-base folder, an
Obsidian vault, a Drive document) is the caller's or a local wrapper
skill's decision, never this skill's own. Return the artifact in chat by
default; write it to a path only when the caller supplies one.

## Skeleton Example

Placeholder values only - never a real project, company, or URL in this
skill's own files.

```markdown
# Source Evidence: <short description of the page/topic>

**Source URL(s):** https://example.com/path/to/page (reached via
https://example.com/path/to/start)
**Access timestamp:** 2026-01-01T12:00:00Z
**Page title(s):** "<Rendered Page Title>"
**Extraction goal:** <the question this pass answers>

## Visited States / Interactions

1. Navigated to https://example.com/path/to/start
2. Clicked tab "Details"
3. Opened accordion "Advanced Options"
4. Advanced pagination to page 2 of an unknown total

## Extracted Content

### <Section/Region Name>

<extracted text, preserving headings/lists/tables/links as structure>

## Screenshots

- <path or reference> - why: <what this screenshot shows that text
  extraction alone wouldn't>

(Omit this section entirely if no screenshot was material.)

## Extraction Notes

<what was skipped/truncated/simplified, and why>

## Gaps / Uncertainties

<content not reached, pagination not exhausted, unclear rendering>

## Recommended Downstream Handling

<narrative-shaped / cumulative-fact-shaped / unclear - and why>
```
