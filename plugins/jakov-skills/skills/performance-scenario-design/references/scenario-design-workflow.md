# Scenario design workflow

## Match the question to a profile

| Question | Profile and evidence |
|---|---|
| Baseline | Small stable workload; establish ordinary timings and correctness. |
| Expected load | Traffic justified by business volumes or observed use; evaluate agreed criteria. |
| Capacity or stress | Controlled increases beyond a target, with stop/recovery conditions and comparable boundary checks. |
| Arrival spike | A stated number of arrivals over a stated window; record which stage becomes busy. |
| Synchronized action | Prepare users, release the selected action within a defined window and measure the actual submit spread. |
| Soak | Sustained representative work long enough to inspect resource or data growth. |
| Regression | Match the earlier user path, load shape, build variables, data state and environment. |

A user count is not a load model. State whether arrivals are externally scheduled or new work depends on earlier completion. Define how waiting, timeouts and dropped arrivals affect achieved load.

## Choose an arrival model deliberately

An open model schedules arrivals independently of earlier work. Set a generator resource ceiling and account for dropped arrivals; otherwise the achieved load can fall below the intended profile. A closed model keeps a population active, so throughput changes with response time and think time. That feedback may represent real use, but it can also reduce offered load as the service slows.

Use the model that represents the question and preserve it for comparisons. Do not translate a user target into a request-rate target without accounting for the workflow. N completed journeys within T seconds implies N/T completed journeys per second over that window; the pressure on each endpoint also depends on how often it is called, pauses, retries, caching and burst timing. This average alone does not define an arrival or submit peak.

## Establish inputs

Inspect relevant requirements, API contracts, current scripts and saved results. Use existing project documentation and available evidence-extraction tools when inputs are missing. Do not require a particular skill or introduce guessed routes, fixtures or credentials.

Record each important input as measured, agreed, proposed or unknown. Keep the source with measured/agreed values. A proposed ramp or threshold can support a reviewable draft while still requiring resolution before a meaningful run.

Name the business decision and the date by which it is needed when that affects the plan. Capture participant counts, entry speed, realistic time per activity and relevant item counts. Include background actors such as staff refreshing lists or dashboards if they form part of the expected peak. Questions that require an owner should name the decision they block and when the answer is needed.

Write a falsifiable expectation before a diagnostic run: which step should saturate first, which metric should change, and which control would challenge that explanation. Keep it a hypothesis until the observations support it.

## Build a prioritized design

1. State the business decision and user-facing success condition.
2. List participant roles, steps, data and authentication dependencies.
3. Choose only the profiles needed to answer that decision; do not enumerate every combination automatically.
4. Include a comparable baseline, then target validation and justified higher steps when the question is capacity.
5. Distinguish arrival spikes from synchronized writes. Think time between joining and submitting changes the pressure on each endpoint.
6. State observation and stop conditions: relevant errors, persistence mismatches, resource exhaustion and recovery checks before escalation. Thresholds come from the team or remain labeled proposals.
7. Define output columns: planned/actual participants, arrival and submit windows, completion, latency by user-facing step, errors, persistence and environment/generator evidence.

Read [data and environment strategy](safety-and-data-strategy.md) for mutating workflows and [the artifact fields](performance-design-artifact.md) when formatting the final design.
