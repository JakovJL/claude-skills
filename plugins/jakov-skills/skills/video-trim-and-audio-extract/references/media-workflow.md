# Detection, cuts and audio options

## Detection is an activity heuristic

ffmpeg silence intervals are inverted into active segments. Nearby segments are merged into blocks and filtered by total activity and activity/span density. This can reject sparse clicks, but it does not recognize speech or decide which meeting the user meant. Music, a playing video and dense background noise can survive the same filters.

For uncertain boundaries, inspect the block table and the user's description. Use an explicit `--end` when several blocks could be relevant. If no block survives, report that result and use a known interval rather than inventing one.

The current helper defaults are tunable starting points, not universal settings:

| Option | Default | Effect |
|---|---|---|
| `--noise-db` | -32 | Lower the threshold to retain quieter activity; raise it toward zero to ignore more low-level sound. |
| `--min-silence` | 1 second | Silence duration used by ffmpeg. |
| `--merge-gap` | 20 seconds | Maximum gap joining activity into one block. |
| `--min-content` | 45 seconds | Minimum total activity in a content block; reduce for short clips. |
| `--min-density` | 0.30 | Minimum activity/span ratio; reduce for pause-heavy material. |
| `--pad` | 2 seconds | Extra retained time after the final accepted block. |

Adjust a relevant parameter and inspect the change rather than stacking unexplained threshold changes.

## Cutting accuracy

Stream copy is the default and avoids re-encoding, but cut boundaries may follow codec/keyframe constraints. A nonzero start is especially sensitive to this. Use `--reencode` when precise video boundaries matter, then inspect the result. Do not promise an exact sub-frame boundary from stream copy.

The source is never an output target. The helper rejects aliases to the source even with `--force`. A failed operation may leave a partial newly created output; inspect it and report the failure rather than presenting it as completed media.

## Audio

`audio` accepts `--start` and `--end`. It re-encodes the chosen interval, while `process` takes audio from the trimmed output unless `--audio-from source` was selected.

The default MP3 uses variable quality. `--mono` downmixes channels; `--for-stt` selects 16 kHz mono as a compact transcription copy. Use that preset only when suitable for the selected transcriber and the task. Preserve the original multichannel recording when channel separation matters.

Measure actual file sizes if size reduction matters. Do not claim a fixed reduction or unchanged transcription accuracy from a preset alone.
