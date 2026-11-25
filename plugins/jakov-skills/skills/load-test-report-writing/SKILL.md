---
name: load-test-report-writing
description: How to turn load-, stress- or performance-test results (Gatling, JMeter, k6, Locust or similar) into reports people can act on - a short report of at most two pages plus a full technical report, with a verdict per run, per-user wait times instead of averages, persistence and server checks, interference on the test environment, like-for-like comparisons, and publishing as clean Google Docs checked page by page. Use it whenever the user asks for a report, summary, "репорт", "отчёт", "сводка" or comparison of load/stress test runs, or wants such results written up for a team, client or manager, even without naming the tool. Not for functional bug reports or test plans.
---

# Writing a load-test report

A load-test report answers one question first: **did the system hold the planned number of users, and how long did people wait?** Everything else is evidence for that answer, and every number in it comes from the run artifacts or a check you ran, never from memory.

If the project under test has its own report skill (for example a project-level `load-test-report` skill), use it as well: it knows where that project's numbers live and how to check its database and environment. This skill is the method and the publishing.

Talk to the user in their language; write the documents in the language they ask for (English when the reports go to a mixed team). Give times in UTC, said once at the top.

## Workflow

1. **Collect the numbers per run**: window, arrival rate, users started / finished / dropped, retries, per-step median, p95, max and errors, per-user wait for the multi-request steps, server and load-generator load. Read `references/metrics.md` first: it says which number answers which question and lists the traps (per-request max is not a user's wait; p95 close to max means many users were slow; averages hide the queue).
2. **Verify persistence.** "Held" means every user who finished has exactly the records they should, nobody else's, no duplicates. Check it in the database or admin, read-only, comparing who should have records with who has them (by count and by a hash of names, never printing personal data). If you cannot check, the report says so.
3. **Check interference** on the test environment for the run windows: other clients in the access logs, other containers' CPU, deploys or restarts, the database and VM baseline before and between runs. Do it soon after the runs; a redeploy wipes container logs. Report it in proportion: name who, when and how much.
4. **Verdict per run.** Use the team's criteria. Without them, propose and label as working criteria: *Held* (everyone finished, allowing a couple of retries; every result saved correctly; no crashes or resource-exhaustion errors) and *No slowdowns* (additionally p95 ≤ 3 s and max ≤ 15 s per user-facing step, first-attempt errors ≤ 1%). Words: "Held, no slowdowns" / "Held with slowdowns" / "Failed".
5. **Write two reports** following `references/report-structure.md`: a short one of at most two pages that opens with the answer, and a full one with everything a developer or DevOps engineer needs (configuration, path, per-step tables, persistence, what happens under load, server, time windows for their dashboards, reliability, recommendations, artifacts). Keep functional bugs out; they are reported separately.
6. **Publish and look.** For Google Docs follow `references/google-docs.md`: markdown → styled HTML with `scripts/md2gdoc.py` → import or update in place → export PDF → render pages with `scripts/pdf2png.ps1` (Windows) → look at every page and fix what you see. The scripts are in `${CLAUDE_SKILL_DIR}/scripts/`; in the references below, `<skill folder>` means `${CLAUDE_SKILL_DIR}`.
7. **Hand off** with titled links, what changed, and what was not verified. Do not post to chats or send documents to anyone yourself.

## Habits that keep a report trustworthy

- State unknowns as unknown ("server response time in those seconds is unknown"), never as zero.
- Label hypotheses and say which data would confirm them.
- Compare with earlier runs only like for like; list what differs (background traffic, build, topology, user count, entry speed) and say what single run would make the comparison clean.
- Check the modelled user path against the real client when the front end may have changed (open the real page and read its network requests).
- When the user asks "is that right?", recompute from the artifacts before answering; correct earlier statements openly.
