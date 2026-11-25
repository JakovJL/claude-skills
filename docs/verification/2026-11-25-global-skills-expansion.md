# Global skill expansion verification

Verified locally on 2026-11-25. The marketplace contains **16 skill entrypoints** in `jakov-skills`: the original reporting skill plus 15 additions. The three excluded candidate-legend folders are absent.

## Completed checks

| Check | Result | Scope |
|---|---|---|
| `python tools/validate_repository.py` | Passed; 16 skills, 0 errors. | Marketplace/plugin names and versions, entrypoints, resource containment/links, selected private markers, Python syntax. |
| Bundled skill-creator `quick_validate.py` | 16 of 16 passed. | Each skill's actual frontmatter and instructions. |
| Python resources in plugins | 6 parsed successfully. | Syntax, not optional dependency importability or native behavior. |
| `python -X utf8 -B -m unittest discover -s tests -v` | 30 passed, 1 skipped, 0 failed. | Replay/traceability helpers, media file protection and mocked HTTP. |
| Independent consumer evaluation | Four requested workflows completed. | Release evidence review, conflict-aware rollback planning, synthetic registry, Russian replay fixture. |
| Original reporting skill diff | Unchanged. | Existing skill and all its resources. |
| `git diff --check` | Passed. | Tracked changes, followed by a staged check before commit. |

The skipped test needs Windows symlink-creation privilege (`WinError 1314`). Direct absolute/drive-relative/parent-traversal cases were executed; the skipped symlink case is not claimed as covered.

## Material fixes included with packaging

- Media output may not alias the original file, including a hard link or the original behind a trimmed intermediate. Transcript JSON obeys no-clobber behavior. Transcription dry run needs neither an API key nor ffmpeg.
- QA investigation follows the requested surface and evidence. It does not mandate unrelated live testing, a fixed reproduction count or automatic issue publication.
- Configuration and delegation methods preserve current task authorization rather than copying obsolete machine/provider defaults.

## Independent evaluation observations

The evaluator used synthetic packets and ran the bundled checkers from an unrelated working directory. The release assessment identified an installer hash mismatch and an old normal shortcut; the rollback plan preserved a later edit to the owned configuration fragment and reported a conflict. A registry with two requirements, two criteria and three test references passed link validation. A Russian replay fixture with one local knowledge file passed integrity validation. Neither result was presented as executed product coverage or a model-quality comparison.

## Runtime boundaries

No recording, private voice profile or real provider account was used.

ffmpeg/ffprobe were unavailable in the task environment, so actual cutting/encoding was not verified. Media checks use synthetic files and a mocked HTTP response. Claude CLI was unavailable in this environment; the native `claude plugin validate` commands were not run. Manifest layout was checked against the current official plugin documentation and by the repository validator.

Available source provenance is recorded in [source notices](../../THIRD_PARTY_NOTICES.md). These checks establish package structure and the described local behaviors, not universal compatibility with every provider, OS or agent host.
