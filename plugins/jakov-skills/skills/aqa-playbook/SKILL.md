---
name: aqa-playbook
description: Investigate UI and API defects with scoped exploratory testing, reproducible steps and raw evidence. Use for bug hunts, defect verification, regression planning or evidence-backed bug reports. Distinguish product defects, upstream behavior and environment failures without treating untested surfaces as passed.
---

# Evidence-backed QA

Investigate the requested surfaces and user paths. Keep the project's URLs, credentials, role definitions, commands and issue registry in project documentation rather than in this global procedure.

## Scope and map

Read project instructions and identify the target build, environment, allowed mutations and available test data. Reuse existing authorization. A bug-report edit does not imply permission for a new live test.

For a broad bug hunt, map relevant surfaces: public UI/API, admin, background jobs, webhooks and integrations. For a narrow report or reproduction, stay on the affected path. Record material untested areas without expanding the assignment to cover everything.

Derive roles from permissions and journeys from state transitions, including empty data, session changes and access to another user's object. Choose checks by risk and the suspected failure, using the [investigation protocols](references/investigation-protocols.md) and relevant [domain checklist](references/domain-checklist.md).

## Investigate

1. Establish expected behavior from requirements, contracts or a justified control. An API response is an observation, not automatically the business oracle for all UI differences.
2. Follow a real user path when the defect concerns UI, authentication, sessions or forms. API shortcuts can diagnose a cause but do not prove that the UI flow works.
3. Preserve raw evidence appropriate to the claim: request/response, screenshot, console output, saved state or a minimal reproducer. Redact credentials and private data.
4. Vary one relevant condition and compare a control when it helps distinguish the cause. Use bounded repeats for intermittent failures and report attempts and outcomes; one failed retry does not clear the original observation.
5. Trace the failing path before proposing a fix. Confirm that the changed code executes on that path. A passing isolated test alone cannot establish that connection.
6. Reconcile the final state after retries, races or writes. Clean up authorized test data and report any remaining changes.

## Classify and report

Use the project's statuses. If none exist, distinguish observed, candidate, reproduced and confirmed; explain the evidence that supports the chosen confidence. There is no universal minimum reproduction count or requirement to recreate a destructive defect.

Consolidate related symptoms when a common cause is supported; retain each affected path and do not merge merely similar-looking failures. Distinguish product, upstream and environment findings.

A report includes environment/build, preconditions, numbered steps, expected and actual behavior, impact, reproducibility, evidence and material limits. Separate severity from priority. Update the requested local registry or report; create external issues only when authorized.

For fix verification, repeat the original failing path and a relevant control, then run checks proportional to the change. Report skipped or unavailable coverage explicitly.
