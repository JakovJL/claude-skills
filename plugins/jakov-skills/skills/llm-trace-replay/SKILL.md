---
name: llm-trace-replay
description: Reconstruct and compare an LLM application's requests from saved traces when investigating prompt, retrieval, latency, routing or answer regressions. Verify frozen messages, settings and knowledge hashes offline before using the application's real request builder or an authorized provider replay.
---

# Reproduce an LLM request from evidence

Start with a specific recorded request or small case set. Capture what was actually sent: messages, provider/model settings, selected knowledge, context limits, truncation decisions, retry attempts and the application's postprocessing. A current prompt file or today's model configuration may differ from the recorded request.

## Freeze the case

Use synthetic examples for public fixtures. Keep private conversations and real model responses in an ignored, user-approved location. Record unknown historical settings as unknown instead of filling them from current defaults.

The portable integrity format and hash convention are in [replay-manifest.md](references/replay-manifest.md). The bundled checker verifies case identity and local knowledge files without loading credentials, importing application code, writing results or making network requests:

```sh
python "${CLAUDE_SKILL_DIR}/scripts/verify_replay.py" cases.json --root ./fixture-root
```

The checker establishes fixture integrity. It does not execute a model, reproduce an application's message builder, or prove the snapshot came from a genuine production trace.

## Reconstruct the application path

Locate the shared production message builder and transport. Feed the frozen state through that path using an application-owned adapter. Compare messages before sending; explain intentional transport additions such as a structured-output suffix. Reject cases that cannot be reconstructed instead of silently rebasing them onto a new prompt or knowledge set.

Keep a recorded-input mode separate from a candidate-change mode. In the first, preserve the original request. In the second, record exactly which prompt, settings, retrieval or history change is under evaluation. Hold other inputs fixed where possible.

## Compare behavior

- Use task-relevant criteria: grounded facts, answer coverage, unsupported claims, useful format, selected evidence and user-visible latency. Keep raw provider output separate from the text produced by application postprocessing.
- Record end-to-end, retrieval, queue, connection/first-token and generation timings separately when available. A fast isolated model call does not establish a fast user action.
- For variable answers, repeat only the cases needed to distinguish a consistent regression from one sample. Report the distribution and relevant failures rather than selecting a favorable answer.
- Count every network attempt, including adaptive and transport retries. Before an authorized live replay, set a request/cost budget, a stop condition and the intended account/route. Do not substitute another provider or paid account silently.

An offline investigation should stay offline. A request to inspect saved traces does not authorize sending their content to a provider. Existing explicit authorization for the current replay remains valid.

Deliver the case IDs/hashes, changed inputs, comparison criteria, observed results and reconstruction gaps. Do not print private prompts merely to demonstrate that verification succeeded.
