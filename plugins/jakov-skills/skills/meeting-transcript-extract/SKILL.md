---
name: meeting-transcript-extract
description: Extract source-backed facts, decisions, action items, risks and open questions from meeting, interview or video transcripts. Preserve speaker and timestamp attribution and use caller-supplied topic categories when given. Use for structured transcript analysis rather than audio transcription.
---

# Extract facts from a transcript

Read the supplied transcript and produce a structured extraction that a reader can trace back to the conversation. Use the user's requested language, categories and scope.

## Select the structure

A supplied taxonomy or output schema takes precedence. Retain its category names and order; put relevant unmatched facts in an unclassified section only when needed. Do not force an educational transcript into a meeting-status template.

Without a supplied schema, use relevant categories from the [extraction schema](references/meeting-extraction-schema.md): facts, decisions, action items, risks, requirements, assumptions and open questions. Scale the structure to the conversation; omit empty sections unless the requested format requires them.

## Extract faithfully

1. Read the entire supplied source or explicitly identify any unread portion. For a large source, process chunks with overlap and reconcile decisions that were revised later.
2. Preserve speaker labels, timestamps or another source location for material items. Use [speaker and evidence rules](references/speaker-and-evidence-rules.md) when labels or ASR text are uncertain.
3. Separate a proposal from an adopted decision, a request from an accepted commitment, and a stated concern from a verified fact.
4. For actions, record the task, owner and deadline only when stated; otherwise mark the missing field. Keep later corrections and conflicting accounts visible.
5. Preserve conditions, quantities, dates and uncertainty. Explain an ambiguity using the source rather than resolving it with a plausible story.

Do not infer personality, motives, diagnoses or performance judgments from conversational remarks. A speaker's statement remains attributed to that speaker unless other evidence confirms it.

## Deliver and follow up

Include source identity, coverage, the requested categories and material evidence gaps. A short summary can lead when useful. Follow the [downstream guide](references/downstream-routing.md) only when the user needs a next step; do not append a routing section mechanically.

Use an available transcript source if the user supplied a video link without text. If none is accessible, state that the transcript is missing. Do not substitute a title or description for the contents of a recording. Audio upload, tracker writes, messages and knowledge-base updates require authorization in the actual task; they are not implied by extracting facts.
