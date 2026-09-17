# 11K Closure Audit — P1R-11 Reproducibility Addendum

**Manuscript ID:** IPM-D-26-07123  
**Audit date:** 2026-09-17  
**Verdict:** **CLOSED — 15/15 blocking checks PASS; 33/33 canonical numerical targets PASS**

## Closure evidence

1. Canonical reconstruction script archived and rerun against preserved inputs; no model training occurs.
2. `P1R11_33_TARGET_VALIDATION.json` reports **33/33 PASS**.
3. The final rerun reproduces the validated v0.5.3 machine outputs byte-for-byte.
4. Probability integrity checks pass for all six preserved arrays; paired-JSD comparison has maximum absolute difference `0.0`.
5. Exact source tables supporting S11–S14 are archived.
6. Exact canonical closure-run environment is captured separately from the historical/reference runtime.
7. Final audited submission files are cryptographically identified; the completed 11K audit reports zero numerical mismatches.
8. The original frozen archive was not written to. Current connected copies of its strict checksum manifest, strict status file, and scientific-source-components manifest match their frozen SHA-256 identities.

## Original-release identity limitation

The original strict forensic record identifies the canonical ZIP as SHA-256 `ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89` and records ZIP CRC/integrity PASS. The canonical ZIP itself is not exposed as downloadable bytes by the currently connected Drive surface, so the closure does not falsely claim a new ZIP-byte rehash. The addendum's `original_archive_unchanged` check is supported by separate-layer write isolation plus fresh hash verification of the connected strict manifest/status/component records.

## Result

The revision-stage addendum is **CLOSED**. The approved past-tense provenance language is now factually supported.
