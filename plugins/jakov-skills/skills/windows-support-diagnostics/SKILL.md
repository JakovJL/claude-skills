---
name: windows-support-diagnostics
description: Investigate a Windows desktop, service, Docker or WSL failure with read-only evidence first, a scoped repair plan and a result check in the affected environment. Use for support diagnosis, collecting a minimal support packet, or designing safe maintenance recipes.
---

# Diagnose the reported Windows symptom

Start with the symptom, affected machine, reproduction and exact error/code. Read project support instructions and existing state before proposing repair. Prefer Windows APIs/CIM and fixed-argument native tools where available; do not turn untrusted text into a shell command.

## Collect the smallest useful evidence

Check relevant OS/build, process/service state, recent error events, component/runtime versions and the actual installation/shortcut target. Use the current task's permitted read-only probes. Separate product defects, missing prerequisites, access restrictions and external-service failures.

An access-denied component query establishes insufficient privilege, not that the component is disabled. Query independent Windows optional components separately so one failure does not hide the other. Resolve a privilege boundary before asserting component state; do not repeatedly launch the same failing check.

A support packet should contain timestamps, the checks run, safe error codes and facts relevant to the symptom. Exclude credential values, unrelated personal files and raw transcripts. Redact command output before sharing it externally.

## Plan an appropriate repair

For each proposed action state its target, expected effect, disruption, privilege requirement, reversibility and how success will be verified. Inspect existing configuration and preserve it by default. Prefer a fixed known recipe to a general command-string executor. Elevate only the operation that needs it, not the whole diagnostic interface.

Do not infer authorization for a restart, feature installation, network reset or cleanup from a request to explain an error. Existing authorization for a specific repair remains valid. Ask only for genuinely missing approval at the affected operation.

## Verify in the affected environment

Read back the component/service state and repeat the original failing action. When a reboot is required, report the repair as awaiting reboot and post-reboot verification until that evidence exists. A successful helper process or a test on another computer does not establish the user's symptom was resolved.

For cleanup, derive and show the resolved target boundary before acting; revalidate paths and skip linked/retargeted items. Use recoverable deletion where appropriate and authorized. Do not clear logs or caches merely to make an error disappear from the report.

Deliver the confirmed diagnosis, performed actions, exact result and the remaining discriminating check. Keep hypotheses labeled when the required environment or evidence is unavailable.
