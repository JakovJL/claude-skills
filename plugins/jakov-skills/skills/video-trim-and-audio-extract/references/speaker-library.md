# Optional local speaker-library helper

Use this only when the task explicitly includes labeling or maintaining a local speaker library and the inputs are authorized. Trimming or extracting audio does not request enrollment.

The helper reads word-level transcript JSON and optional hand-labeled text. Stable anonymous labels are a valid result. Preserve ambiguity when identity is not established by reliable supplied evidence; similarity scores are candidate matches, not proof of identity.

```sh
python "${CLAUDE_SKILL_DIR}/scripts/speaker_voice_library.py" --help
python "${CLAUDE_SKILL_DIR}/scripts/speaker_voice_library.py" map-labels --json recording_transcript.json --labeled verified_labels.txt
python "${CLAUDE_SKILL_DIR}/scripts/speaker_voice_library.py" --library "local-voice-library" identify --audio recording.mp3 --json recording_transcript.json --candidates "Participant A,Participant B"
```

`map-labels` proposes an alignment against a verified labeling of the same recording. Inspect ambiguous or mixed-speaker passages rather than treating a high aggregate alignment as authority to enroll every segment.

Enrollment and matching need ffmpeg, numpy, soundfile, sherpa-onnx and a compatible ONNX speaker model. The helper reports a missing model location and source URL; it does not download the model automatically. Confirm model suitability and usage terms before obtaining it.

`enroll-pair` assumes a true two-person recording with an established known voice. That assumption fails for one-sided capture, another meeting, media playback or a third participant. Do not use the helper's complement heuristic as evidence that an unknown voice belongs to a named person.

Store samples and embeddings in an authorized local private directory outside the repository and synchronized document stores. Do not distribute the library, model artifacts, real transcripts or voice samples with this skill. Respect the participants' consent and the task's retention/deletion requirements.
