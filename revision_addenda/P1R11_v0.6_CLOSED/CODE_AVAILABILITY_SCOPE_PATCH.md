# Code Availability — Two-Layer Provenance Scope Patch

**P1R-11 addendum status: CLOSED.**

## Submission-final wording

> The original frozen reproducibility release documents the primary RQ1–RQ4 analyses and the sensitivity/exploratory analyses included when that release was frozen. Its legacy status fields, including `new_statistical_tests: false`, apply to that original analysis layer only. Revision-stage post hoc sensitivity analyses are documented separately in the versioned P1R-11 reproducibility addendum, which preserves the original release unchanged and provides the corresponding scripts, machine-readable outputs, source tables, and cryptographic manifests.

## Machine-readable counterpart

`manifests/P1R11_ADDENDUM_MANIFEST.json` records:

- `original_archive.scope_note.legacy_field = "new_statistical_tests"`;
- `original_archive.scope_note.legacy_value = false`;
- scope limited to the original frozen analysis layer;
- `original_archive.original_archive_modified = false`;
- `original_archive.original_archive_unchanged = true`.

The canonical original ZIP SHA-256 is retained as the recorded release identity. The ZIP bytes were not exposed on the connected Drive surface, so this closure does not claim a fresh ZIP-byte rehash.
