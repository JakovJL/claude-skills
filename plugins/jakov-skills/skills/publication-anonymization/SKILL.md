---
name: publication-anonymization
description: Prepare source files, documentation, test fixtures and technical reports for public sharing by removing personal or confidential details while preserving useful measurements and evidence boundaries. Use for a private-to-public repository review, sanitized examples, or publishing technical case studies.
---

# Prepare technical material for public sharing

Establish the intended audience and publication surface: current tracked files, an export, packaged artifacts or repository history. Inspect the existing Git state and preserve unrelated staged/unstaged work. Preparing current files does not silently authorize rewriting history or publishing them.

## Inventory before replacing

Search relevant source, fixtures, active documentation, archived reports, screenshots and generated/distributed artifacts. Look for personal paths, recording identifiers, real quotes, customer/employer references, account IDs, credentials and cross-file duplicates. Use local secret-scanning tools when available; compare findings against the existing baseline without printing secret values.

Review context before replacement. Synthetic dates, intentional negative-test values and placeholder credentials may be test inputs rather than personal data. Preserve what the test checks. Avoid bulk substitutions that silently weaken assertions or change protocol payloads.

## Preserve the technical meaning

- Use consistent neutral identifiers for the public material. Keep any reversible mapping and original excerpts outside the public tree in a protected local location.
- Preserve aggregate measurements, request order, configuration relationships and limitations. Do not present newly written examples as original observations.
- Mark reconstructed/synthetic fixtures explicitly. Summarize private conversation content when a technical failure class can be explained without verbatim speech.
- Use portable example paths and make clear when a documentation-only identifier is not the name of a real downloadable artifact.

Choose a proportionate anonymization method for the intended data. Replacing names alone may leave identifying combinations in small datasets or images; inspect the result in context.

## Verify the selected surface

Repeat searches for the selected markers and locally known secret values without exposing those values in logs. Review the diff for changed measurements, lost qualifications and damaged fixtures. Run checks relevant to modified behavior and render visual artifacts when they are part of the export.

Report exactly which surface was checked. A clean current tree does not establish clean Git history, release archives or remote copies. Handle history rewriting, deletion and publication as distinct authorized actions. Keep source attribution and existing license notices; anonymization is not a license or redistribution audit.
