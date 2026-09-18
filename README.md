# IGAR Paper 1 — Reproducibility Repository v1.1.0

Reproducibility materials accompanying the **final resubmission version** of:

**Characterizing Weak-Label Disagreement in Indonesian Digital Public-Service Application Reviews: Transformer Sensitivity to Supervision-Source Choice**

Authors:

- **Idham Khaliq**, Master's Program in Informatics, Faculty of Industrial Technology, Universitas Ahmad Dahlan — ORCID: 0009-0004-5214-5583
- **Uturestantix**, Department of Management, Faculty of Economics and Business, Universitas Cenderawasih — ORCID: 0000-0001-8321-8731

## Publication role

Release **v1.1.0** is the reproducibility companion for the manuscript's final resubmission package.

The current `main` branch uses the terminology and interpretation boundaries of the final resubmission manuscript. Historical internal workflow identifiers such as `P1R-11` and earlier phrases such as `revision-stage` remain only where needed to identify preserved historical paths, manifests, or archived provenance records.

This narrative alignment does **not** alter the frozen computational record, trained models, test predictions, primary RQ1–RQ4 estimates, post hoc machine outputs, source tables, or cryptographic identities.

## Provenance layers

### v1.0.0 — original frozen primary-analysis release

The original reproducibility release remains unchanged and identifiable by tag `v1.0.0`. It contains the frozen computational record for the primary RQ1–RQ4 analyses and the sensitivity/exploratory analyses included when that layer was frozen.

- Historical release status: **CLOSED / PASS — STRICT FORENSIC**
- Canonical strict ZIP SHA-256: `ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89`
- Scientific source component-set SHA-256: `bc5ec1a72c7168be6deba93036cb444748611f3a6e3735d47ffb9f479c779530`
- Canonical checksum-manifest SHA-256: `c1a594f0a9138e458345581dd5087977ce903e50bf28016161940ac57b6dfef2`

Historical `new_statistical_tests: false` fields or equivalent statements apply only to this frozen v1.0.0 analysis layer. They do not describe the later post hoc analyses added for the final resubmission.

### v1.1.0 — versioned post hoc reproducibility addendum

Release **v1.1.0** preserves v1.0.0 unchanged and adds a separate versioned reproducibility addendum documenting targeted **post hoc sensitivity and diagnostic analyses** reconstructed and rerun from preserved RQ4 test predictions and associated metadata.

The original analytic samples, trained models, test predictions, and primary RQ1–RQ4 estimates were retained unchanged. No model retraining, new model architecture, additional weak-supervision source, new data collection, or change to the frozen cohort or train/validation/test assignments was introduced.

The historical internal workflow identifier for this addendum is `P1R-11`; it is retained in archive paths and filenames for traceability.

Closure status:

- addendum version: **0.6-closed**
- blocking checks: **15/15 PASS**
- numerical validation targets: **33/33 PASS**
- exact addendum ZIP SHA-256: `ce69cda9003425b7a5c326beb1531d27efb6149591416be32beee933dfd8356b`

Historical archive path:

`revision_addenda/P1R11_v0.6_CLOSED/`

Exact packaged copy:

`revision_addenda/IGAR_Paper1_P1R11_Reproducibility_Addendum_v0.6_CLOSED.zip`

## Scientific scope and interpretation

Neither weak-supervision source is treated as ground truth. The study characterizes **weak-label disagreement** and evaluates its association with Transformer sensitivity to supervision-source choice.

The paired RQ4 design substitutes the complete weak-supervision target pathway while holding review text, data partitions, architecture, classifier initialization, training order, and configuration fixed within seed. The result is therefore interpreted as an association with supervision-pathway choice, not as a pure causal source-identity effect.

The final manuscript reports:

- source disagreement: **41.35%**; Cohen's κ = **0.334**;
- mean three-seed JSD: **0.0519** for agreement and **0.4065** for disagreement;
- primary difference: **β = 0.3546**, 95% CI **[0.3426, 0.3665]**;
- polarity-only sensitivity: **β = 0.2788**;
- full usable-text source corpus singleton sensitivity: **β = 0.2985**.

The full source corpus contains **617,722** reviews and **397,731** normalized duplicate-text groups because the 26 missing-text records retain unique grouping identifiers. The **617,696-review usable-text pool contains 397,705 groups**. Singleton sensitivity is defined from this full usable-text duplicate mapping, not from uniqueness within the RQ4 test set.

Within-supervision accuracy/F1 values are learnability diagnostics rather than source-correctness estimates. The post hoc analyses qualify the magnitude and composition of the primary association; they do not establish that one weak-supervision source is correct or superior.

## Historical-artifact interpretation note

The frozen v1.0.0 notebook, documentation, status files, and the `historical_execution/` records intentionally preserve terminology and workflow states that were current when those artifacts were created. They may therefore contain an earlier working title, earlier `severity` language, or statements such as `new_statistical_tests: false` that apply only to the original frozen layer.

Those historical statements must not be interpreted as the terminology or full analysis inventory of the final resubmission manuscript. The separate v1.1.0 addendum is the authoritative provenance record for the later post hoc sensitivity and diagnostic analyses.

## Structure

- `canonical_archive/` — original v1.0.0 strict-final ZIP; preserved unchanged.
- `reproducibility/IGAR-Paper1-Reproducibility/` — original frozen reproducibility layer.
- `revision_addenda/P1R11_v0.6_CLOSED/` — closed versioned post hoc addendum, retaining its historical internal path.
- `docs/` — historical human-readable reproducibility documentation.
- `back_matter/` — availability/declaration templates.
- `CITATION.cff` and `.zenodo.json` — current repository metadata aligned to the final resubmission narrative.
- `PUBLIC_RELEASE_STATUS.json` — current release-role and provenance record.
- `MANIFEST_PUBLIC_RELEASE_v1.0.0.sha256` — preserved manifest for the original release.
- `MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256` — manifest for the tagged v1.1.0 release snapshot.
- `MANIFEST_MAIN_FINAL_RESUBMISSION.sha256` — checksum manifest for current `main` after final-resubmission narrative alignment.

## Data

The raw IGAR dataset is **not redistributed** in this repository.

Dataset:

- Mendeley Data, Version 3
- DOI: `10.17632/7zryc6k76z.3`
- License: CC BY 4.0
- Data article DOI: `10.1016/j.dib.2026.112708`

The released dataset-provided translation and VADER variables were analyzed as released; they were not regenerated for this study.

## Verification

The versioned release manifests identify the tagged release snapshots. Because `main` contains narrative-only alignment updates made after the v1.1.0 tag, the tagged v1.1.0 manifest is not a checksum manifest for current `main`.

Verify the current final-resubmission-aligned `main` state with:

```bash
sha256sum -c MANIFEST_MAIN_FINAL_RESUBMISSION.sha256
python tools/verify_v1_1_repository.py --repo .
```

The immutable scientific archives remain independently verifiable:

```bash
sha256sum canonical_archive/IGAR-Paper1-Reproducibility_STRICT_FINAL.zip
sha256sum revision_addenda/IGAR_Paper1_P1R11_Reproducibility_Addendum_v0.6_CLOSED.zip
```

Expected:

```text
ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89
ce69cda9003425b7a5c326beb1531d27efb6149591416be32beee933dfd8356b
```

Internal addendum verification:

```bash
cd revision_addenda/P1R11_v0.6_CLOSED
sha256sum -c manifests/SHA256SUMS.txt
python tools/verify_addendum.py
```

## License

Repository software and original release documentation are provided under the MIT License. The IGAR dataset is not included and retains its own CC BY 4.0 license.
