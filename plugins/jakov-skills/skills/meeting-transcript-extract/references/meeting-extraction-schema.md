# Transcript extraction structure

## Choose the shape

A user-supplied schema or taxonomy takes precedence. Retain category names and ordering, include relevant source locations, and collect genuinely unmatched facts separately when needed. Do not rename the taxonomy into a generic meeting report.

For a normal meeting extraction, choose the relevant categories:

| Category | Include | Distinguish from |
|---|---|---|
| Facts | Explicit statements, quantities and context with attribution. | Independent verification of the statement. |
| Decisions | A choice the conversation actually adopted, with conditions. | A suggestion or unresolved alternative. |
| Actions | Concrete task, accepted owner and stated deadline. | A request without acceptance or an invented due date. |
| Risks and concerns | Stated risks and their conditions. | A diagnosis or prediction added by the analyst. |
| Requirements and preferences | Constraints or desired behavior, with who stated them. | An analyst's recommendation. |
| Assumptions | Inputs participants explicitly treated as uncertain. | Confirmed facts. |
| Open questions | Unresolved questions, conflicts and missing evidence. | A question that was answered later in the same source. |

Omit empty categories unless the target format requires them. For a topical educational transcript, supplied topic buckets may fit better than decisions and tasks.

## Source and evidence

Identify the transcript/recording, supplied coverage and speaker-label limitations. Retain timestamps or another source location for material extracted items. Flag passages that depend on unclear ASR or attribution.

If sources disagree, preserve the attributed accounts and explain the unresolved difference. A later explicit correction can supersede an earlier statement; record the correction rather than leaving two incompatible facts without context.

## Compact example

Source: supplied transcript, 00:00-12:00; automatic speaker labels.

- Decision, 08:14, Speaker B: retain the current workflow for this release, pending the compatibility check.
- Action, 08:32, Speaker A: perform that check. Deadline was not stated.
- Open question, 09:10: the transcript does not resolve whether the external dependency supports the required format.

These are synthetic examples of structure, not evidence about a real meeting.
