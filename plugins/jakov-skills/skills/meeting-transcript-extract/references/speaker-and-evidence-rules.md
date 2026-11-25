# Speaker And Evidence Rules

## Preserve speaker attribution

When the transcript labels speakers (names, roles, "Speaker 1"/"Speaker
2", diarization tags), preserve that attribution in the extraction note -
who said what matters for downstream judgment (whose account a risk is,
who made a decision, who owns an action item). Do not flatten multiple
speakers into an unattributed "it was discussed that..." when the source
actually distinguishes them.

When speaker labels are unclear, inconsistent, or auto-generated with
visible errors (e.g. a diarization tool that mislabels turns), say so
explicitly rather than presenting a guessed attribution as reliable. Use
a confidence note like `speaker attribution uncertain past this point` if
the transcript's labeling degrades partway through, rather than silently
carrying a possibly-wrong label forward.

## Evidence quality and confidence

Tag extraction items with a confidence/evidence-quality note whenever it's
anything less than a clear, directly-stated fact from a clearly-labeled
speaker. Useful distinctions:

- **Clear** - directly stated, clearly attributed, no ASR/transcription
  ambiguity.
- **ASR-uncertain** - the transcript itself shows signs of
  automatic-speech-recognition error (garbled words, nonsensical
  fragments, a term that's almost certainly a mis-transcription of a
  proper noun or domain term). Extract the likely intended meaning only
  if it's reasonably inferable, and flag it as ASR-uncertain either way.
- **Speaker-uncertain** - the content is clear but which speaker said it
  is not (crossed labels, unlabeled turn, group discussion with no
  per-speaker breakdown).
- **Inferred** - not stated directly, but a reasonable derivation from
  what was said (state the derivation briefly so a reader can judge it
  independently).
- **Single-account** - reported by only one participant, with no
  corroboration from others present, and where whose account it is
  matters for how much weight to give it (e.g. one person's description
  of another team's behavior).

An item with no quality note is implicitly "clear" - reserve the tags for
where they add real information, not on every single line.

## Limits on inference

Do not infer or state, beyond what the transcript actually supports:

- **Personal motives** - why someone did something, what they "really"
  meant, or what they were "actually" feeling, unless they said so
  themselves.
- **Performance judgments** - whether someone is doing well or poorly,
  competent or not, unless the transcript contains an explicit assessment
  (and if so, attribute it as that person's/speaker's stated assessment,
  not as an objective conclusion this extraction reached).
- **Commitments beyond what was said** - if someone described an
  intention or a possibility, do not upgrade it to a firm commitment in
  the extraction; if someone made a firm commitment, do not soften it into
  a mere possibility either. Match the transcript's own certainty level.

A people/relationship signal (see the schema's section 9) should read as
an observation of what was said or how something was described, not as a
conclusion about the person. "Mentioned feeling out of the loop on the
deployment decision" is a signal; "seems disengaged from the project" is
an unsupported judgment - don't write the second kind.

## Handling multiple accounts of the same event

When multiple speakers describe the same event differently, record both
accounts with their attribution rather than silently picking one or
blending them into a single merged version. If the transcript itself
doesn't resolve which account is more accurate, the extraction note
shouldn't resolve it either - note the discrepancy as-is (an Open
Question or a flagged item in Risks/Concerns, whichever fits) rather than
presenting one account as settled.
