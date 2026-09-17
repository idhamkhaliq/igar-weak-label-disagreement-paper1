# P1R-11 Reproducibility Addendum — v0.6 CLOSED

**Manuscript ID:** IPM-D-26-07123  
**Status:** **CLOSED**  
**Closed:** 2026-09-17T15:46:02Z

This package is the closed revision-stage provenance layer for P1R-11. It does not replace or rewrite the original frozen reproducibility release.

## Closure summary

- **15/15 blocking closure checks PASS.**
- **33/33 canonical P1R-11 numerical targets PASS** in the archived closure rerun.
- `P1R11_REPRODUCED_RESULTS.json` is byte-identical to the validated v0.5.3 output (SHA-256 `5aa8288b3cf44ce1ddc01ace3a2fbe8deb05ec6a6ecf61993e4c0694aad6d5bc`).
- `P1R11_33_TARGET_VALIDATION.json` reports `all_33_pass: true` (SHA-256 `ca75a8fd20e075a89c630ddf39b19ddccb1c0ce5bab27174b00592909c292ee3`).
- Source tables supporting Supplementary Tables S11–S14 are archived under `supplement_sources/`.
- The exact canonical closure-run environment is archived under `closure_environment/`; it is **not** relabeled as the exact historical P1R-11 environment.
- Final submission-file hashes and the completed 11K numerical cross-check are archived under `submission_crosscheck/`.

## Original frozen release boundary

The P1R-11 workflow did not write to the original frozen archive. During closure, the current connected-Drive copies of `checksums_STRICT.sha256`, `REPRODUCIBILITY_STATUS_STRICT.json`, and `SCIENTIFIC_SOURCE_COMPONENTS_STRICT.json` were re-downloaded and matched their frozen SHA-256 identities. The canonical original release ZIP hash remains the recorded release identity:

`ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89`

The ZIP bytes themselves are not exposed by the connected Drive surface, so this package does **not** claim a fresh ZIP-byte rehash. This limitation is recorded explicitly rather than hidden.

## Verification

From the extracted addendum root:

```bash
sha256sum -c manifests/SHA256SUMS.txt
python tools/verify_addendum.py
```
