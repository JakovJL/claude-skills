---
name: performance-scenario-design
description: Design load, stress, spike, soak, capacity or regression scenarios from API contracts, user workflows and traffic evidence. Use before implementing a test to define load shape, data, pacing, observability and pass/fail criteria. Planning does not authorize a test run.
---

# Performance scenario design

Turn the performance question into a reviewable design that an engineer can implement in the project's chosen load tool. Keep proposed traffic and thresholds visibly separate from measured or agreed inputs.

## Ground the question

Read the relevant parts of [scenario design](references/scenario-design-workflow.md). Establish the decision the test must support: expected-load validation, finding a breakpoint, arrival spike, synchronized submission, endurance or comparison with an earlier build.

Inspect existing scripts, API contracts, user journeys and saved runs before asking for missing inputs. The sibling [api-source-intake](../api-source-intake/SKILL.md) can help gather a contract; an existing project contract is equally suitable.

State the environment, user-facing workflow and data dependencies. Unknowns can remain in a draft with their effect on execution stated; they do not require guessing or blocking unrelated planning work.

## Design

Use the [design artifact](references/performance-design-artifact.md) as a field guide, combining related scenarios in one comparison table when that makes the decision clearer.

1. Define scope, participant roles, request sequence, business success and what remains outside the test.
2. Define arrival model, participants, ramp, duration, think time and the window of any synchronized action. A fast arrival ramp does not establish simultaneous submission.
3. Match comparisons by user path, build, data state, load shape and environment. Retain a comparable baseline; list differences that prevent attribution.
4. For capacity questions, include justified steps above target with transition, stop and recovery conditions. A passed highest step proves at least that level, not an exact limit.
5. Define data creation, reuse, authentication, cleanup and how results will be reconciled to participants. Read [data and environment strategy](references/safety-and-data-strategy.md) for mutating workflows.
6. Define metrics and pass/fail criteria at the relevant user-facing step. Include completion, errors, persistence and generator health alongside latency. Label proposed SLOs and assumptions as proposals.
7. Specify observability windows, clock/timezone, correlation IDs and evidence required for the final report.

For a service investigated from outside, use [controlled bottleneck experiments](references/black-box-bottleneck-experiments.md) to design discriminating checks rather than naming a cause from one timing. When browser performance is in scope, use [frontend workload design](references/frontend-workload.md) to represent the intended audience and measure when each step becomes usable.

Use natural language and a profile table before committing to engine syntax. If the user also requested implementation, carry the approved design into that work; [engine handoff](references/downstream-engine-handoff.md) lists the information it needs.

## Boundaries

Honor explicit restrictions on tests, mocks, target access and network calls. Saved-result analysis and a request for tomorrow's plan do not authorize a run today. Existing task authorization remains valid; ask again only when the target, intensity or side effects exceed it.

Do not invent production volumes, question counts, fixture readiness, rate limits or team-approved thresholds. Keep each material assumption next to the scenario it affects and identify the smallest evidence or decision that resolves it.
