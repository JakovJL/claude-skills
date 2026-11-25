# Controlled bottleneck experiments

Use this when the planning question includes finding the limiting component and source code or internal telemetry is incomplete. Designing a probe does not authorize executing it. Prefer existing artifacts when the task prohibits target access or tests.

## Gather a useful baseline

From authorized sources, identify the real user request sequence, endpoint timings and payload sizes, cache and connection conditions, deployment/build and data state. Client bundles and documentation can reveal candidate routes, but verify the route and its side effects before using it as a workload.

Record errors with their safe response bodies and timestamps, not only status codes. Preserve the distinction between an observed error class and a proposed underlying cause. For example, a connection-acquisition timeout supports a pool-wait observation; it does not by itself identify which transaction held the connections.

Do not assume a header or framework fingerprint establishes the full topology. Session acceptance, sticky routing and an apparently idle host are weak evidence for instance count or process parallelism without corroboration.

## Design a comparison that separates explanations

| Condition | Purpose | What to keep comparable |
|---|---|---|
| No added workload | Establish the ordinary timing distribution. | Build, data, cache and connections. |
| Candidate endpoint workload | Test whether that work coincides with another route slowing. | Arrival profile, duration and observation window. |
| Comparable control workload | Challenge explanations based only on client connections or a shared proxy. | Concurrency/rate, connection reuse and response characteristics as far as feasible. |
| Recovery observation | Establish whether health returns and how long it takes. | No hidden background load or intervening deployment. |

A background sampler can measure a small route beside the candidate workload when authorized. An edge response may supply another comparison only after establishing which layer actually serves it; a 404 is not inherently outside the application. Use repeated or reordered blocks when needed to reduce warmup, drift or order effects, within the run budget.

Differences among routes can narrow a bottleneck hypothesis. They do not prove event-loop blocking, database contention or serialization without further evidence. Likewise, subtracting a rough network baseline from TTFB is an estimate with connection and scheduling assumptions, not a direct measurement of server execution time.

## Separate dimensions

- Compare read-heavy work and write-heavy work when their effects need isolating. A read-only endpoint can still be expensive or trigger background work.
- Rank latency beside payload size and the request path. A small response can hide an expensive query; a large response can spend time in serialization, compression or transfer.
- Track generated data and response growth. An identical profile run against a larger dataset may perform different work.
- Compare planned with achieved arrivals and generator health before attributing a throughput plateau to the service.
- Mark the first affected user step, time-to-error, the last healthy interval and recovery. Preserve the exact observation windows for server correlation.

## Request evidence that discriminates the hypothesis

Use available read-only monitoring or ask the owner for the relevant exported interval. Explain the purpose of each request:

- Per-core/process CPU and event-loop or worker-queue timing for a suspected execution bottleneck.
- Pool size, active/waiting connections, acquisition timing and query/transaction spans for a suspected database wait.
- Queue depth, consumers and delivery timing for asynchronous work.
- Proxy/downstream timing and timeout configuration for delayed or rejected requests.
- Deployment, restart and unrelated-traffic evidence for interference.

Correlate by time and request identity. After a change, retain the same meaningful baseline and inspect whether the limit moved rather than assuming that fixing one bottleneck removes the next one. Feed observations into the existing reporting workflow; this reference does not define a second report format.
