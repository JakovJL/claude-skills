# Which number answers which question

## Per request vs per user

Load tools report per request: median, p95, max for each request name. Users experience steps that may contain several requests in a row (a page that fires three API calls before it shows). A user can wait on more than one of them, so **a user's wait can exceed the slowest single request**. When you write "the page opens in up to N seconds", compute it per user from the tool's per-user journal or log (time from the step's first request to its last response), not from the request table.

Say which "share of users" you mean: "waited > 3 s on any entry step" and "waited > 3 s to open the page" are different numbers.

## Percentiles, not averages

Under a burst the distribution is usually two groups: users served at once and users stuck in a queue. A mean mixes them into a number that describes nobody. Report median, p95, maximum and the share of users over 3 s / 10 s / 15 s. When more than 5% of users are slow, p95 falls inside the slow group and sits close to the maximum: that means many users were slow, not a measurement error. Non-engineers understand "61% of people waited more than 3 s, up to 18 s" better than "p95 14.3 s".

## Queue or rejection

For slow requests, compare when they were sent with when they finished (seconds after the first arrival). Sent during the burst and finished right after it, at a steady rate, is a queue. When the queue outlasts a proxy or load-balancer timeout, users get 502/503/504 instead.

## Who produced an error

Look at the failed responses' headers and bodies: a load balancer or proxy (e.g. `Server: awselb/2.0`, nginx error pages) versus the application. AWS ALB answers 504 after about 10 s when it cannot open a connection to the target, and 502 when the target closes or resets the connection. Count application 5xx separately from the access logs.

## Server saturation

Sum the CPU of all containers on a host during the burst and compare with the host's cores. Near the limit, containers compete for the same cores: adding containers on the same VM does not add capacity, and CPU limits that add up to more than the cores hide that. Metrics endpoints that time out during the burst mean those seconds are unknown, not zero.

## Load generator

Client-side times are trustworthy only while the generator stays under about 80% CPU during the measured window. Above that, say client-side delays may be overstated; server- and proxy-produced errors are unaffected.

## Model realism

Note where the scenario differs from people: missing think time (typing a form, drawing a signature), sequential calls the browser sends in parallel, caches a real browser would or would not have. Say in which direction each difference moves the result.

## Comparing runs

Background traffic during the test (staff pages, other users, probes) can change entry times by an order of magnitude. Only compare runs whose user count, entry speed, background, build and topology match, or list every difference and call the result an observation, not a regression.
