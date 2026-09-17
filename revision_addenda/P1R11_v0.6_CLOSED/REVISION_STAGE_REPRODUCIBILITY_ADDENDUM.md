# IGAR Paper 1 — Revision-Stage Reproducibility Addendum (P1R-11)

**Manuscript:** *Characterizing Weak-Label Disagreement in Indonesian Digital Public-Service Application Reviews: Transformer Sensitivity to Supervision-Source Choice*  
**Manuscript ID:** IPM-D-26-07123  
**Addendum scope:** P1R-11 revision-stage post hoc sensitivity analyses  
**Status:** **CLOSED — 15/15 blocking checks PASS; 33/33 numerical targets PASS**  
**Date prepared:** 2026-09-17

---

## 1. Purpose and relationship to the original reproducibility archive

This addendum documents analyses introduced during revision after the original Paper 1 reproducibility archive had been frozen. It is deliberately maintained as a **second provenance layer** and must not overwrite, rewrite, or silently replace any file in the original frozen archive.

The provenance model is therefore:

1. **Original frozen archive** — supports the original RQ1–RQ4 samples, trained models, test predictions, primary estimates, and originally prespecified sensitivity/exploratory analyses.
2. **Revision-stage reproducibility addendum** — supports the P1R-11 post hoc sensitivity analyses, the exact source tables used for Supplementary Tables S11–S14, and the associated revision-stage scripts, outputs, manifests, and hashes.

The original analytic samples, trained models, test predictions, and primary RQ1–RQ4 estimates were retained unchanged. During revision, targeted post hoc sensitivity analyses were added using the preserved RQ4 test predictions and associated metadata. No model retraining, new model architecture, additional weak-supervision source, new data collection, or change to the frozen cohort or train/validation/test assignments was introduced.

### Scope of status fields in the original frozen archive

The original frozen archive contains status fields that describe the state of the project **at the time that archive was frozen**. In particular, any original manifest field equivalent to `new_statistical_tests: false` applies only to the original frozen RQ1–RQ4 analysis layer and its then-existing sensitivity/exploratory analyses. It must not be interpreted as a claim that no additional analyses were later introduced during manuscript revision.

The revision-stage addendum therefore records an explicit machine-readable scope note for this legacy field while leaving the original archive byte-for-byte unchanged. The addendum, not a rewritten original manifest, is the authoritative provenance record for the P1R-11 post hoc sensitivity analyses.

This addendum is **not** a replacement preregistration and does not retroactively label revision-stage analyses as prespecified. All analyses documented here must remain explicitly identified as post hoc sensitivity or diagnostic analyses.

---

## 2. Immutable boundary inherited from the original archive

The addendum inherits the following fixed scientific objects from the original archive and must verify their identity before any revision-stage computation is accepted:

- full source corpus: **617,722 reviews**;
- frozen RQ4 cohort: **150,000 reviews**;
- train/validation/test assignments: **105,000 / 22,500 / 22,500**;
- frozen RQ4 test set: **22,500 reviews**;
- agreement reviews in the frozen test set: **13,196**;
- disagreement reviews in the frozen test set: **9,304**;
- six preserved three-class test-probability matrices:
  - Model-R seed 42;
  - Model-R seed 123;
  - Model-R seed 2026;
  - Model-V seed 42;
  - Model-V seed 123;
  - Model-V seed 2026;
- class order: **Negative, Neutral, Positive**;
- test-row ordering;
- `row_id`, `duplicate_group_id`, weak-source R label, weak-source V label, disagreement indicator `D`, and other metadata used by the original RQ4 analysis.

The addendum must fail closure if any preserved probability matrix, row order, class order, test-set identity, or required metadata mapping cannot be verified against the archived source identities.

---

## 3. Integrity reproduction before revision-stage analyses

Before P1R-11 analyses are considered reproducible, the addendum must reproduce the original headline RQ4 quantities from the preserved predictions and metadata.

### Required reproduction targets

| Quantity | Required value |
|---|---:|
| Test N | 22,500 |
| Agreement N (`D=0`) | 13,196 |
| Disagreement N (`D=1`) | 9,304 |
| Mean cross-source JSD, agreement | 0.0519 |
| Mean cross-source JSD, disagreement | 0.4065 |
| Primary cluster-robust coefficient | β = 0.3546 |
| Primary coefficient, unrounded verification value | β = 0.35456868 |
| Adjacent-category disagreement (`S=1`) mean JSD | **0.4409** |
| Direct Negative–Positive (`S=2`) mean JSD | 0.3195 |

Probability-integrity checks must additionally confirm:

- all values are finite;
- no NaN or infinite values occur;
- every probability row sums to approximately one within numerical precision;
- all six arrays contain the same 22,500 test rows in the same order;
- class ordering is identical across arrays;
- archived file identities/hashes match the original reproducibility archive.

**Closure rule:** if the original quantities cannot be reproduced to the archived/reporting precision, stop and do not certify the revision-stage addendum.

---

## 4. Revision-stage analyses and reported outputs

The values below are the **reported P1R-11 outputs that the closure run must reproduce exactly or to the manuscript-reported precision**. They are not substitutes for the scripts, machine-readable outputs, and hashes required in Sections 6–8.

### 4.1 Within-source run-to-run variability

The six within-source seed pairs are:

- R42–R123;
- R42–R2026;
- R123–R2026;
- V42–V123;
- V42–V2026;
- V123–V2026.

Within-source comparisons vary random seed and the associated initialization/training order, whereas each paired cross-source comparison is matched within seed and changes the supervision target. The within-source analyses therefore serve as a **broad reference for ordinary run-to-run predictive variability**, not as a mathematical upper bound.

Reported cross-source / combined-within-source JSD ratios among disagreement reviews:

| Evaluation subset | Ratio |
|---|---:|
| Full frozen test set | **81.03** |
| Polarity-only subset | **49.73** |
| Full-source singleton subset | **59.60** |

The closure package must preserve the underlying per-pair and aggregated within-source JSD summaries used to derive these ratios, not only the ratios themselves.

### 4.2 Polarity-only / Neutral-free sensitivity

Evaluation-stage restriction: retain only reviews for which both weak sources assign Negative or Positive. The original models remain three-class classifiers and are **not retrained**.

| Quantity | Reported value |
|---|---:|
| Polarity-only N | **15,385** |
| β | **0.2788** |
| 95% CI | **[0.2610, 0.2966]** |
| Retained magnitude relative to primary β | **78.6%** |

This analysis does not estimate performance under a binary retraining objective.

### 4.3 Full-source singleton sensitivity

Singleton status is defined from the authoritative full usable-text duplicate mapping, not uniqueness within the 22,500-review test set.

| Quantity | Reported value |
|---|---:|
| Full-source singleton N | **14,551** |
| β | **0.2985** |
| 95% CI | **[0.2928, 0.3041]** |
| Retained magnitude relative to primary β | **84.2%** |

For interpretation, the earlier sensitivity analysis that removed only the largest 1/5/10 duplicate-text clusters changed β by at most **2.06%**, whereas excluding every review belonging to any repeated-text group attenuated the estimate by **15.82%**. These analyses answer different repeated-text questions and must remain separately identified.

### 4.4 Joint singleton × polarity restriction

| Quantity | Reported value |
|---|---:|
| Joint subset N | **9,561** |
| β | **0.2553** |
| 95% CI | **[0.2467, 0.2639]** |
| Retained magnitude relative to primary β | **72.0%** |

This is a supplementary joint sensitivity diagnostic, not a new primary criterion.

### 4.5 Target learnability and shared-label diagnostics

Reported class-specific and shared-label diagnostics include:

- Model-R mean rating-derived Neutral F1: **0.1069**;
- on shared Negative/Positive agreement cases, three-class accuracy difference **V − R = −2.45 percentage points**;
- after restricting the evaluation decision to Negative versus Positive:
  - Model-R accuracy: **97.60%**;
  - Model-V accuracy: **97.12%**;
  - difference **V − R = −0.48 percentage points**.

The shared-label subset is agreement-selected and easier than the full test set. It must not be presented as an overall benchmark or as evidence that one weak-supervision source is correct.

### 4.6 Source-specific uncertainty diagnostic

On polarity-agreement reviews, the reported Model-R / Model-V entropy ratio is:

| Distribution used | Entropy ratio R/V |
|---|---:|
| Original three-class predictive distributions | **1.4719** |
| Negative/Positive-renormalized distributions | **1.3403** |

These diagnostics show asymmetric predictive diffuseness/target learnability and are used to qualify interpretation. They do not convert the analysis into a source-accuracy comparison.

### 4.7 Directional composition and agreement-cell heterogeneity

For the `S=1` disagreement category:

- total `S=1` disagreement reviews: **6,666**;
- polarity-to-VADER-Neutral transitions: **5,862 (87.94%)**;
- weighted mean JSD for polarity-to-VADER-Neutral transitions: **≈ 0.4800**;
- weighted mean JSD for rating-Neutral-to-polarity transitions: **≈ 0.1556**;
- approximately **95.7%** of the weighted JSD mass of `S=1` came from transitions toward VADER Neutral.

The revision therefore treats the previous categorical-distance pattern primarily as a **directional and weak-label class-composition result**, not as ordinal error severity.

For the Neutral/Neutral agreement cell:

| Quantity | Reported value |
|---|---:|
| N | **449** |
| Mean cross-source JSD | **0.370** |
| Median cross-source JSD | **0.394** |

This diagnostic is important for interpretation: weak-label disagreement remains a useful triage signal, but agreement does not guarantee low supervision-source sensitivity.

---

## 5. Mapping to revised manuscript and Supplementary Tables S11–S14

The addendum must contain the exact machine-readable source outputs from which the revised tables were generated.

| Supplementary table | Reproducibility role |
|---|---|
| **S11** | Artifact-integrity and reproduction audit for preserved RQ4 predictions/metadata and reproduction of the original primary RQ4 quantities |
| **S12** | Within-source seed-JSD, cross-source comparison, polarity-only run-to-run cross-check, and related magnitude summaries |
| **S13** | Class-specific learnability, shared-label performance, entropy/max-confidence diagnostics |
| **S14** | Polarity-only, full-source singleton, joint singleton × polarity, directional-composition and agreement-cell sensitivity outputs as applicable to the final approved supplement |

If the final Supplementary Material uses a slightly different allocation of rows across S11–S14, the **final archived source-table mapping must follow the actual submitted supplement**, not this planning table. The manifest must record the exact final filenames and table destinations.

---

## 6. Required addendum package structure

The following structure is recommended for closure. Existing established filenames may be retained, but every final artifact must be listed in the manifest.

```text
revision_stage_addendum/
├── REVISION_STAGE_REPRODUCIBILITY_ADDENDUM.md
├── scripts/
│   ├── [P1R-11 analysis script(s)]
│   └── [table-generation / verification script(s)]
├── outputs/
│   ├── [machine-readable P1R-11 result files]
│   ├── [integrity-audit output]
│   └── [exact numerical summaries]
├── tables/
│   ├── [S11 source table]
│   ├── [S12 source table]
│   ├── [S13 source table]
│   └── [S14 source table]
└── manifests/
    ├── P1R11_ADDENDUM_MANIFEST.json
    ├── P1R11_ADDENDUM_STATUS.json
    └── SHA256SUMS.txt
```

The original frozen archive remains outside this directory and must not be modified by addendum scripts.

---

## 7. Manifest requirements

`P1R11_ADDENDUM_MANIFEST.json` must record, at minimum:

- addendum version and date;
- manuscript ID;
- original frozen archive version / DOI / release identifier as applicable;
- an explicit `original_archive_scope_note` identifying the legacy `new_statistical_tests: false` field, limiting it to the original frozen analysis layer, and recording `original_archive_modified: false`;
- identity and SHA-256 of each preserved input actually read by the revision-stage scripts, including the RQ3 primary table, RQ3 singleton-sensitivity table, and frozen RQ4 cohort parquet when those files are read to derive revision-stage membership or metadata;
- identity and SHA-256 of each revision-stage script;
- identity and SHA-256 of each generated machine-readable output;
- identity and SHA-256 of each S11–S14 source table;
- test-row-order hash used by the analysis;
- class order;
- Python and relevant library versions for the closure run, including `pyarrow` because Parquet inputs are part of the preserved revision-stage dependency chain;
- command(s) used to execute the analyses;
- final status: `OPEN` or `CLOSED`;
- closure timestamp when and only when all checks pass.

Earlier OPEN drafts used `null` for hashes that had not yet been verified. In this CLOSED release, all archived scripts, machine outputs, source tables, environment captures, provenance evidence, and submission cross-check records carry real SHA-256 identities; no guessed hash values are used.

### Checksum portability requirement

`SHA256SUMS.txt` must use **paths relative to the addendum archive root**, not creator-machine absolute paths. A downloaded and extracted package must therefore be verifiable with a standard command such as `sha256sum -c SHA256SUMS.txt` from the directory containing that checksum file.

---

## 8. Closure checks for P1R-11 / 11K

The addendum may be marked `CLOSED` only when all of the following pass:

- [x] original frozen release remains unmodified by the P1R-11 workflow; current strict checksum/status/component manifests match their frozen identities (the canonical ZIP hash is retained as recorded identity; no fresh ZIP-byte rehash is claimed);
- [x] addendum manifest contains an explicit scope note for the original `new_statistical_tests: false` field and contains no inherited status field that contradicts manuscript Section 2.14;
- [x] six preserved probability matrices are identified and their archived hashes verified;
- [x] test-row-order identity/hash is verified;
- [x] probability integrity checks pass;
- [x] original RQ4 quantities reproduce to the required precision;
- [x] every revision-stage closure/reproduction script is archived;
- [x] every revision-stage machine-readable output is archived;
- [x] exact S11–S14 source tables are archived;
- [x] all addendum artifacts except the checksum manifest itself are listed in the portable SHA-256 checksum manifest (self-exclusion avoids a checksum cycle);
- [x] manifest paths match actual files;
- [x] manuscript/Supplement/Response/Cover numerical values agree with archived outputs and final audited rounding;
- [x] no revision-stage analysis is mislabeled as prespecified;
- [x] no statement implies model retraining or a new supervision source;
- [x] `P1R11_ADDENDUM_STATUS.json` records `status = "CLOSED"` after all checks passed.

All boxes above now pass. The addendum status is therefore **CLOSED**.

---

## 9. Submission-facing provenance wording after closure

Section 8 is complete. Submission-facing documents may use the approved past-tense language stating that the revision-stage analyses **are documented** in a separate versioned addendum.

### Approved integrity statement

> The original analytic samples, trained models, test predictions, and primary RQ1–RQ4 estimates were retained unchanged. During revision, we added targeted post hoc sensitivity analyses using the preserved RQ4 test predictions and associated metadata. No model retraining, new model architecture, additional weak-supervision source, new data collection, or change to the frozen cohort or train/validation/test assignments was introduced.

### Approved archive sentence after closure

> The original reproducibility archive remains preserved unchanged. The revision-stage analyses are documented in a separate versioned reproducibility addendum containing the analysis scripts, machine-readable outputs, source tables for Supplementary Tables S11–S14, and cryptographic manifests.

### Approved Code Availability scope wording after closure

> The original frozen reproducibility release documents the primary RQ1–RQ4 analyses and the sensitivity/exploratory analyses included when that release was frozen. Its legacy status fields, including `new_statistical_tests: false`, apply to that original analysis layer only. Revision-stage post hoc sensitivity analyses are documented separately in the versioned P1R-11 reproducibility addendum, which preserves the original release unchanged and provides the corresponding scripts, machine-readable outputs, source tables, and cryptographic manifests.

### Historical pre-closure wording (no longer active)

The following future/conditional wording applied only before closure and is retained here for audit history:

> The revision-stage analyses will be documented in a separate versioned reproducibility addendum.

The corresponding historical interim Code Availability wording was:

> The original frozen reproducibility release documents the primary RQ1–RQ4 analysis layer. A separate versioned addendum is being finalized for the revision-stage post hoc sensitivity analyses; the original release will remain unchanged.

Do **not** use the past-tense archive sentence in the submission-final Response, Section 2.15, Supplementary Table S11 note, or Code Availability statement until closure is complete.

---

## 10. Interpretation lock

The addendum documents reproducibility; it does not change the scientific guardrails:

- use **weak-label disagreement**, not verified label error;
- neither rating-derived nor translation-mediated VADER labels are ground truth;
- Model-R versus Model-V accuracy/macro-F1 are source-conditioned diagnostics and must not be used to rank supervision-source correctness;
- within-source seed comparisons are a reference for ordinary run-to-run variability, not a formal upper bound;
- polarity-only results are evaluation-stage restrictions of the original three-class models;
- singleton results remove repeated-text structure from evaluation but do not create a new training experiment;
- shared-label diagnostics apply to an agreement-selected subset and are not an overall benchmark;
- entropy describes predictive diffuseness/uncertainty, not correctness;
- revision-stage analyses are post hoc sensitivity analyses and must remain labeled as such.

---

## 11. Current release state

The revision-stage archive layer is now cryptographically closed. The archived closure rerun reproduces all 33 canonical numerical targets, the exact S11–S14 source files are present, the closure environment is captured, the final submission package has been cross-checked, and all 15 blocking closure checks are true.

**ADDENDUM STATUS: CLOSED — 15/15 BLOCKING CHECKS PASS; 33/33 NUMERICAL TARGETS PASS**

Closure timestamp: `2026-09-17T15:46:02Z`. Past-tense submission wording in Section 2.15, Supplementary Table S11, Response to the Editor, Cover Letter, and Code Availability is therefore unlocked.

The original frozen release remains a separate provenance layer. Current connected copies of its strict checksum/status/component manifests match their frozen identities. The canonical ZIP SHA-256 is retained as the recorded release identity; because the canonical ZIP bytes are not exposed by the connected Drive surface, no new ZIP-byte rehash is claimed.


## 11K provenance recovery note (v0.5)

During 11K, Project-history records were recovered showing that P1R-11A/B/D/E/F/C, the locked Decision Gate, and 11G had already been executed from the preserved probability matrices and associated metadata, without model retraining. These historical records trace all 33 canonical revision-stage targets to the stages in which they were computed. The exact original raw P1R-11 script/output bundle was not recovered as standalone files. A reconstructed closure script was therefore labeled explicitly as reconstructed from the documented analysis specification, archived, rerun against the preserved inputs, and required to reproduce all canonical targets before closure. That requirement is now satisfied: 33/33 targets pass.
