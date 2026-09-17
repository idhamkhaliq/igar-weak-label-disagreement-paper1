# FINAL CLOSURE REPORT — P1R-11

**Manuscript ID:** IPM-D-26-07123  
**Addendum:** v0.6-closed  
**Closed at:** 2026-09-17T15:46:02Z

## Decision

**CLOSED.** All 15 blocking checks are true and the archived numerical validation reports 33/33 PASS.

## 15 blocking checks

1. `original_archive_unchanged` — **PASS**
2. `original_archive_scope_note_present` — **PASS**
3. `six_probability_hashes_verified` — **PASS**
4. `test_row_order_verified` — **PASS**
5. `probability_integrity_pass` — **PASS**
6. `primary_rq4_reproduced_from_preserved_inputs_in_closure_run` — **PASS**
7. `revision_scripts_archived` — **PASS**
8. `machine_outputs_archived` — **PASS**
9. `s11_s14_sources_archived` — **PASS**
10. `canonical_closure_environment_archived` — **PASS**
11. `all_sha256_present` — **PASS**
12. `manifest_paths_match_files` — **PASS**
13. `submission_numbers_crosschecked_against_final_p1r11_package` — **PASS**
14. `no_prespecified_mislabeling` — **PASS**
15. `no_retraining_or_new_supervision_implied` — **PASS**

## Numerical closure

- Primary beta reproduced: **0.35456868010652**.
- Agreement / disagreement mean JSD: **0.05190023 / 0.40646891**.
- Paired-JSD comparison to the preserved original paired-JSD artifact: maximum absolute difference **0.0**.
- Canonical target validation: **33/33 PASS**.

## Submission cross-check

The final audited manuscript, Supplement, Response to the Editor, and Cover Letter are cryptographically identified in `submission_crosscheck/P1R11_SUBMISSION_NUMERICAL_CROSSCHECK.json`. The completed 11K audit found **0 mismatches across 103 Supplement values** and **0 mismatches across 30 canonical cross-document values**; observed differences were reporting precision only.

## Original frozen release

The original release remains a separate layer. Its current connected strict checksum manifest, strict status file, and scientific-source-components manifest match their frozen SHA-256 identities. The canonical ZIP SHA-256 `ae8eb3d4...` remains a recorded release identity; no new ZIP-byte rehash is claimed because the ZIP bytes are unavailable on the connected Drive surface.
