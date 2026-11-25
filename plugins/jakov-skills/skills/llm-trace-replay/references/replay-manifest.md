# Portable replay integrity format

Use JSON with `schema_version: 1` and a nonempty `cases` list. Each case has:

| Field | Meaning |
|---|---|
| `id` | Unique nonempty case ID. |
| `messages` | Nonempty JSON array of message objects, each with a nonempty string `role`. Preserve every message field exactly. |
| `messages_sha256` | SHA-256 of the canonical JSON representation of `messages`. |
| `settings` | JSON object containing the frozen non-secret request options. An empty object is valid when there were no recorded options. |
| `settings_sha256` | SHA-256 of the canonical JSON representation of `settings`. |
| `knowledge` | Optional array of `{ "path": "kb/topic.md", "sha256": "..." }`. Each path identifies a regular file beneath `--root`; hashes cover its original bytes. |

Canonical JSON is UTF-8 encoded `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)`. List order is significant. Object key order is not. Hash before storing the snapshot; do not recalculate the expected hash merely to make a changed fixture pass.

Reference hashes are exactly 64 hexadecimal characters. Absolute paths, parent traversal and resolved links outside the fixture root are rejected. The checker does not URL-decode paths. Secret-bearing settings such as `api_key`, `authorization`, `access_token`, `refresh_token`, `password`, `client_secret` and `cookie` are rejected by key; this is a guard against common mistakes, not a complete secret scanner.

The checker reports case counts, IDs and error categories, never message contents or settings values. Its exit codes are `0` for valid fixtures, `1` for inconsistent cases, and `2` for an unreadable or malformed input/invalid root. No live-replay mode is bundled: actual requests remain with the application's verified transport and task-specific authorization.
