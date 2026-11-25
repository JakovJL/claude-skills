# Frontend workload design

Use this when the decision concerns how a real person experiences the workflow, including first entry, interactive steps and behavior during a backend peak.

## Represent the audience

Select device/browser, viewport, network, CPU conditions, session state and cache state from the intended audience. First-time mobile visitors and returning desktop staff can require different profiles. Treat emulated throttling as a controlled approximation; it does not establish behavior on a physical phone or a different browser engine.

Use representative profiles or clearly labeled sensitivity cases instead of presenting a tool's preset as the actual audience. Record hardware/browser versions and the applied conditions so a comparison can be repeated.

## Measure the step the user needs

- Define when the required control is visible, enabled and usable, and how that state is observed. A page-load event alone does not prove the task can start.
- Capture relevant navigation/rendering and interaction timings alongside the custom step-ready measurement.
- Record transferred and decoded resource sizes by type, dependent requests, failed resources and main-thread work when available.
- State whether the measurement includes DNS/TLS, authentication, lazy loading and navigation between steps.

A similar duration under two network profiles can suggest a non-network limit but does not establish a server cause. Inspect the request waterfall, CPU work and cache behavior before drawing that conclusion.

## Compare conditions

Distinguish a cold first visit from a warm return visit. Establish an idle baseline and, when authorized and part of the plan, observe the same browser journey during a backend load step. Keep time windows synchronized and record other traffic or deployments.

Use enough bounded repetitions to characterize the variability that matters, recording sample count, failures and run conditions. Choose a statistic that answers the decision; a small set of repetitions should not be presented as a stable tail percentile.

Use team criteria or clearly labeled proposed criteria for the chosen audience and step. If relying on external metric bands, verify their current definition and applicability rather than copying an old preset threshold into the design.

## Useful hypotheses to inspect

An unnecessarily large shared bundle, inactive-language downloads, oversized imagery, unbounded list data, a slow global widget or a third-party render dependency can be concrete suspects when the waterfall supports them. Record which resource or dependency blocks the required user action and the evidence that would confirm an improvement.

Keep browser results distinct from protocol-level load results: one measures the user's rendered path and the other measures an offered server workload. Neither alone establishes the other's achieved behavior.
