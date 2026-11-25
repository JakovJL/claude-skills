# Report structure and wording

## Short report (at most two pages, checked on the rendered PDF)

```
# <System> load test before <event>, <date> (summary)

**<The answer in one bold sentence: holds N users or not.>** <Saved results, losses, duplicates.>
<When delays appear, with per-user numbers.> <Where it breaks.>

## What we tested
- Environment as deployed on <date>: build, topology, size.
- Users: who they are (pre-registered / new), how many, a fresh data set per run.
- The user path in one line; background traffic running at the same time.
- Retries and timeouts as modelled.
Criteria. Held: ... No slowdowns: ...

## Results
| Users / entry window | Entries per second | Did not finish | Waited > 3 s | Slowest step, p95 | Maximum | Verdict |
<one paragraph: persistence; which steps stay fast>

## Where the bottleneck is
3-4 bullets: which requests are slow and what serves them; the queue; what has headroom; proxy errors; no application 5xx / restarts (if true).

## What this means for <event>
2-3 numbered points: what is safe, what to avoid, what to change.

## Limitations
At most 3 bullets: scope and number of runs; generator; functional bugs reported separately.

Times are in UTC. Full report: <link>
```

## Full report, in this order

Conclusion (answer + run table with run IDs) · Configuration (component table, host, database) · User path (step table, what happens on error) · Background, data and users · Criteria · Response time by step (median or p95 / max table; first-attempt errors; proxy error table) · Persistence (table) · What happens under load (queue table, where the delay is, root cause only if proven) · Server (peak table) · Time windows for dashboards and logs (UTC table) · Reliability (generator, other traffic, repeatability, any formal tool verdict explained in one line, configuration not changed) · Recommendations (numbered) · Artifacts (run folders and what each holds; no local links in shared documents).

Headings without typed numbers; refer to sections by name.

## Wording

- The first sentence of the document and of each section is its point, with a number.
- Per user over per request; say which share you mean.
- Plain words, sentences under 25 words, no emoji, no "significantly/robust/leverage", at most one dash per paragraph.
- Unknown is written as unknown; hypotheses are labelled.

## Leave out

- Functional bugs (errors that occur at any load). One neutral line may explain why the tool's formal verdict is worse than the participant verdict.
- Personal data: names, emails, ID numbers, tokens, device IDs.
- Local file links in documents for other people; give folder names as text.
- Comparisons with environments you did not test, unless asked.
