---
name: safe-config-migrations
description: Plan, review or implement changes to existing local configuration files while preserving unrelated settings, detecting concurrent edits and recovering from partial application. Use for installers, agent setup tools, config migrations, managed fragments and rollback behavior.
---

# Change existing configuration without losing newer work

Read the actual files and applicable configuration layers before proposing a change. Identify the owner of each field or fragment, parsing format, file encoding, merge semantics and effective precedence. A syntactically valid file can still be ignored or overridden by another layer.

## Build a reviewable plan

For each resource record its canonical path, whether it existed, the original content hash, the specific owned fields/fragments, the proposed changes and an inverse operation. Show a redacted structural diff. Keep original bytes in protected local backups when restoration needs them; ordinary logs and previews must not contain secret values.

Do not replace hook arrays, imports or lists with a generic deep merge unless their actual semantics permit it. Preserve unknown keys. A detected executable, hook or connection is not automatically trusted or authorized for execution.

## Apply with conflict checks

1. Validate the complete proposal before the first write. Refuse unsupported formats, ambiguous ownership and linked/retargeted paths that violate the intended target boundary.
2. Compare each current resource with the preview's original hash immediately before changing it. A changed resource requires a refreshed plan; do not overwrite it using stale approval.
3. Persist a transaction record before effects. Track prepared, applying, verified and unresolved steps with sufficient information for recovery after restart.
4. Use a temporary file and same-directory replacement for an individual file when supported. Read back and validate the actual result. Multiple file replacements do not form one atomic transaction.
5. Serialize operations that affect the same resources. On failure, inspect actual state before deciding what applied; an exception does not prove there was no effect.

Existing authorization for the exact changes remains valid. If target, scope or effects change materially after preview, make that difference reviewable before proceeding.

## Restore only owned changes

Walk applied steps in reverse order. Restore an original value only when the current value still matches the recorded after-state for that owned portion. Preserve later manual edits and report concrete conflicts. An originally absent file may be removed only if it remains wholly owned and matches the recorded after-state. Do not recursively delete user directories as cleanup.

Separate local config restoration from external account/grant revocation; one does not silently perform the other. Test interruption, second application, stale preview, manual edits after application, missing backup and linked-path cases on temporary profiles before using real configuration.

Report desired state, observed effective state, applied steps, restored steps and unresolved conflicts separately. Neither a valid JSON document nor a successful write establishes that the receiving application loaded the settings.
