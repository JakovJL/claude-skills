---
name: realtime-latency-diagnosis
description: Diagnose growing delay in streaming, audio, transcription or other real-time pipelines by separating input capture, queueing, service work and user-visible output. Use when throughput benchmarks look healthy but the live interface falls behind, or performance differs across target machines.
---

# Find where live delay accumulates

Trace the actual path from input arrival to visible output. Confirm the changed code executes on that path. Map timestamps for capture, admission, queue entry, service start/end, delivery and rendering; use a monotonic clock for elapsed durations and preserve correlation/session IDs across boundaries.

## Separate the measurements

- **Service time:** work performed by the engine, excluding input pacing and queue wait.
- **Queue wait and growth:** how long work waits, outstanding work over time, arrival rate versus processing capacity.
- **End-to-end delay:** age of the input represented by the text/frame/result the user can currently see.
- **Shutdown tail:** admitted work that was completed, drained, cancelled or lost when a session stopped.

An empty queue at one instant does not establish a low maximum delay. A missing final summary may be an instrumentation/lifecycle gap. Check generation changes, cancellation order and retired workers before concluding that work caught up or disappeared.

For overlapping channels, define the denominator explicitly: processing two simultaneous ten-second tracks is a ten-second live workload. Summing their durations can make an overloaded system appear faster than real time. Keep unpaced throughput and paced live behavior separate.

## Compare configurations deliberately

Record the actual resolved backend/device, runtime/model hashes, relevant settings, topology and driver information. An affinity mask is permission to run on processors, not proof of which cores or how many threads were active. Do not copy a CPU mask or infer a GPU/CPU policy from another machine.

Use identical synthetic or authorized samples, warm-up policy, channel pairing and context settings. Change one suspected factor at a time; record repeat variability, failures and output-quality checks alongside speed. Keep diagnostic settings local to the tested child process/profile and restore the prior state after an authorized change.

Before running a benchmark, check task limits on devices, providers, load and network. Saved-result analysis can identify a missing measurement without launching new tests.

## Close with evidence

Explain the measured bottleneck, competing explanations and the next discriminating observation. Attach results to the tested machine and workload. Validate a proposed fix on the affected target and, when relevant, in the real native interface with physical inputs. A local synthetic benchmark supports a diagnosis or tool check; it does not substitute for unavailable target-machine acceptance.
