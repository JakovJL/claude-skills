---
name: windows-release-verification
description: Audit or verify a Windows desktop release from the source revision through the built installer and the application launched by its real shortcut. Use for release readiness, packaged-versus-source regressions, stale installations, installer smoke checks, or a release that passed unit tests but fails on a user's computer.
---

# Verify a Windows desktop release

Establish which artifact the user will run, then connect evidence to that exact artifact. A source test, a packaged executable test and an installed-shortcut test answer different questions.

## Establish the release inputs

Read the project's build and publishing instructions. Record the intended revision, dirty-tree scope, version source, target OS/architecture, build command and artifact locations. Inspect what the build cleans or temporarily modifies before starting it. Keep logs and evidence outside directories the build deletes; preserve existing artifacts without silently moving or deleting user files.

Check whether a running application reads code or assets from the checkout. Branch switches and frontend rebuilds can change files beneath that process. Follow the project's isolation rules; an extra worktree is useful only when permitted. Do not close an active application that may be recording or processing user work merely to simplify a check.

## Verify the chain

Choose checks appropriate to the change and available authorization:

1. **Source:** run the relevant tests/build in the documented environment. Record the revision and any intentional uncommitted inputs.
2. **Packaged executable:** verify startup, bundled assets, runtime discovery and a representative changed flow using an isolated data profile. Check frozen-resource paths and writable-data locations rather than assuming the development layout survives packaging.
3. **Exact installer:** install the actual candidate artifact in a disposable account, VM or approved test location. Check launch, upgrade behavior, shortcuts and uninstall as applicable. Do not uninstall the owner's working application as a smoke test.
4. **Normal launch:** inspect the shortcut target and running process path. Exercise the changed behavior in the native window at realistic sizes, including tray/minimize/restore where relevant. Browser-preview captures alone do not verify native-window behavior.
5. **Artifact identity:** compare version metadata, file size and SHA-256 with the manifest/checksum for the candidate. After an authorized publication, verify the uploaded/downloaded artifact independently.

Use synthetic settings and files for fresh-install checks. Keep physical-device, screen-reader, conferencing, provider and target-machine checks distinct; report only those actually performed. Discover the application's documented profile override rather than inventing an environment variable.

## Readiness result

Return a compact table: source revision, candidate version, executable/installer identity, checks performed, failures and acceptance gaps. Attach each result to its environment and artifact hash. Distinguish a failed gate from an unavailable tool or a check outside scope. A successful launch does not establish that every feature works.

Build verification does not itself authorize a source push, release publication or deployment. Preserve any approval already given for the current task; request missing authorization only at the actual external action.
