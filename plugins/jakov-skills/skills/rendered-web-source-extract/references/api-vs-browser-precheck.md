# API-Vs-Browser Precheck

## Purpose

Run this before opening a browser tool at all. Browser extraction is
slower and more fragile than a structured API/client path whenever one
exists - a page's renderer/DOM can change and break a scrape, while a
structured response stays stable, keeps real IDs/links, and needs far
fewer round-trips. This file is the check that keeps browser extraction
a deliberate choice, not a default habit.

This is a project-level judgment call, not something this skill decides
in isolation - some projects already have their own explicit rule for
this (an internal reference describing which sources have a credentialed
script and which don't). Defer to that rule if the current project has
one; this file is the generic fallback procedure for projects that don't.

## The Check

1. **Look for the current project's own instructions first** - a root
   `CLAUDE.md`/`AGENTS.md`/`README`, or an existing project-local
   reference whose job is exactly this decision (an "access rules" or
   "source access" style document, if the project has one). If such a
   document exists, read and follow it instead of re-deriving the
   decision here.
2. **Check for an existing script/client for this domain** - a
   `scripts/`, `tools/`, or similarly-named utility directory in the
   current project is the first place to look. A domain that already has
   a working, credentialed client script is almost always the API-first
   case; use it rather than reaching for the browser out of habit.
3. **If no script exists yet, weigh whether this access pattern will
   recur.** A source with a real, documented API and a plausible reuse
   case (the same kind of page/domain will likely need reading again)
   is worth a one-time credential/client setup, mirroring the existing
   scripts in step 2 - that investment pays for itself after the second
   use. A genuine one-off read of a source with no reuse case does not
   need this investment; use the browser for it and move on.
4. **If genuinely unsure whether an API exists**, a quick, low-cost check
   (does the site publish API/developer documentation, does its own admin
   console mention one) is worth doing before defaulting to a browser -
   but do not spend disproportionate effort standing up a brand-new
   integration just to avoid one browser session.
5. **An already-open or already-authenticated browser session is not by
   itself a reason to prefer it.** Re-run this check even when a browser
   happens to be open for another reason - convenience in the moment
   doesn't outweigh a documented, more reliable API path.

## When Browser Is The Right Call

- No suitable API/client exists for the source, and setting one up isn't
  justified for a one-off read.
- The source is a genuinely interactive UI - a form flow, a dashboard
  whose state depends on live interaction, content gated behind tabs/
  accordions/pagination/"load more"/modals that a structured endpoint
  doesn't expose.
- The rendered/visual state itself is the evidence being captured (a UI
  bug, a layout, a live dashboard reading at a point in time) - not just
  a means of reaching text a structured source could otherwise provide.

## Missing Browser Capability

If no Playwright MCP/browser tool is available in the current session:

1. Check whether the current project provides its own local rendered-
   fetch script (same places as step 2 above) - use it if so.
2. Otherwise, report the missing rendering capability. Return any useful static evidence with its coverage limits, without claiming that unvisited interactive states were captured.

**Do not substitute a raw HTTP/WebFetch-style fetch and present it as
equivalent to a rendered extraction.** A plain fetch does not execute
client-side rendering, does not reveal tab/accordion/pagination/modal
content, and cannot capture visual state - treating its output as if it
were the rendered page misrepresents the evidence to whatever reads it
downstream.

## Raw HTTP/WebFetch As Triage Only

A quick raw fetch (does this URL even resolve, roughly what is this page
about, is there a redirect/login wall) is a reasonable first sanity check
before deciding whether browser extraction is worth doing at all. It is
**not** an acceptable substitute for the actual evidence artifact once
that artifact is meant to be committed into a knowledge base or otherwise
relied on - unless the page is confirmed genuinely static, with no
interactive or rendered-dependent content relevant to the extraction
goal, in which case browser extraction would only add overhead for no
real benefit.
