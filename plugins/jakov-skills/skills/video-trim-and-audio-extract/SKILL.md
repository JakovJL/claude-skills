---
name: video-trim-and-audio-extract
description: Trim a named local recording, inspect audio-activity blocks, extract MP3 audio, or optionally transcribe through an explicitly requested ElevenLabs upload. Use for media preparation and selected time ranges; keep the source intact and distinguish an activity heuristic from known speech boundaries.
---

# Prepare a local recording

Work only on the file and operation the user requested. Preserve the source and use a separate output. The bundled helpers use Python 3.10 or newer and ffmpeg/ffprobe for local media operations; check that those tools exist before using them.

## Choose the operation

```sh
python "${CLAUDE_SKILL_DIR}/scripts/video_tail_trim.py" detect "recording.mp4"
python "${CLAUDE_SKILL_DIR}/scripts/video_tail_trim.py" cut "recording.mp4" --end 00:24:36
python "${CLAUDE_SKILL_DIR}/scripts/video_tail_trim.py" audio "recording.mp4" --start 00:02:00 --end 00:24:36
python "${CLAUDE_SKILL_DIR}/scripts/video_tail_trim.py" process "recording.mp4" --end 00:24:36
```

- `detect` reads audio activity and writes nothing. Use it when the end is uncertain; inspect the proposed blocks before choosing a cut.
- `cut` creates a trimmed media file. `audio` creates only the MP3. `process` creates both, so use `audio` when only sound was requested.
- An explicit requested interval supplies the cut boundary; do not introduce a confirmation gate merely because automatic detection is available.
- Outputs default to the source folder. Pass the relevant output option when the user chooses another destination. Existing outputs require `--force`, which is appropriate only when overwriting that output is authorized.

Read [detection and cutting details](references/media-workflow.md) for thresholds, keyframe behavior and audio options. Verify output duration and the requested boundary when tools permit. A successfully created file does not prove the intended speech was retained.

## Optional transcription

The `transcribe` subcommand uploads the selected file to ElevenLabs. It never runs as part of `process`. Reuse explicit upload authorization in the task; otherwise get permission for that file before sending it. Do not infer authorization to upload from a local trimming request.

```sh
python "${CLAUDE_SKILL_DIR}/scripts/video_tail_trim.py" transcribe "recording_audio.mp3" --language ru --dry-run
```

Dry run does not read credentials or contact the provider. A real call reads `ELEVENLABS_API_KEY` or `--api-key-file`; do not place a key in an argument or report. Verify current model support, file limits, cost and account data handling before relying on them for an upload. The helper's default model is configurable with `--model`; it is not a promise about provider availability.

Use `--timestamps` for source locations and `--save-json` when word-level data is needed. Keep outputs private to the authorized destination. For local, explicitly requested speaker-label work, read [speaker-library handling](references/speaker-library.md); do not enroll voices or infer a person's identity as a side effect of trimming or transcription.

Local regression checks use only synthetic files and mocked HTTP: `python "${CLAUDE_SKILL_DIR}/scripts/test_video_tail_trim.py"`. They verify output protection and dry-run behavior; they do not establish encoding quality or provider compatibility.
