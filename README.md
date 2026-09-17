# IGAR Paper 1 — Reproducibility Repository v1.1.0

Reproducibility materials for:

**Characterizing Weak-Label Disagreement in Indonesian Digital Public-Service Application Reviews: Transformer Sensitivity to Supervision-Source Choice**

Authors:

- **Idham Khaliq**, Master's Program in Informatics, Faculty of Industrial Technology, Universitas Ahmad Dahlan — ORCID: 0009-0004-5214-5583
- **Uturestantix**, Department of Management, Faculty of Economics and Business, Universitas Cenderawasih — ORCID: 0000-0001-8321-8731

## Repository versioning

This repository now preserves **two explicitly separated provenance layers**.

### v1.0.0 — original frozen primary-analysis release

The original public reproducibility release remains unchanged and identifiable by tag `v1.0.0`.
It contains the frozen computational record for the primary RQ1–RQ4 analyses.

- Historical release status: **CLOSED / PASS — STRICT FORENSIC**
- Canonical strict ZIP SHA-256: `ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89`
- Scientific source component-set SHA-256: `bc5ec1a72c7168be6deba93036cb444748611f3a6e3735d47ffb9f479c779530`
- Canonical checksum-manifest SHA-256: `c1a594f0a9138e458345581dd5087977ce903e50bf28016161940ac57b6dfef2`

The v1.0.0 statement that no new statistical tests were introduced applies to preparation of that historical release. It must not be read as describing the later revision-stage P1R-11 analyses.

### v1.1.0 — revision-stage reproducibility release

Release v1.1.0 adds the **P1R-11 revision-stage reproducibility addendum** without replacing or rewriting the original frozen layer.

The addendum contains targeted post hoc sensitivity analyses reconstructed and rerun from preserved RQ4 test predictions and associated metadata. The original analytic samples, trained models, test predictions, and primary RQ1–RQ4 estimates remain unchanged.

No model retraining, new model architecture, additional weak-supervision source, new data collection, or change to the frozen cohort or train/validation/test assignments was introduced.

P1R-11 closure status:

- addendum version: **0.6-closed**
- blocking checks: **15/15 PASS**
- numerical validation targets: **33/33 PASS**
- exact addendum ZIP SHA-256: `ce69cda9003425b7a5c326beb1531d27efb6149591416be32beee933dfd8356b`

Browse the revision layer at:

`revision_addenda/P1R11_v0.6_CLOSED/`

The exact packaged copy is retained at:

`revision_addenda/IGAR_Paper1_P1R11_Reproducibility_Addendum_v0.6_CLOSED.zip`

## Structure

- `canonical_archive/` — original v1.0.0 strict-final ZIP; do not modify.
- `reproducibility/IGAR-Paper1-Reproducibility/` — original frozen reproducibility contents; do not rewrite as P1R-11 material.
- `revision_addenda/P1R11_v0.6_CLOSED/` — closed P1R-11 revision-stage layer.
- `docs/` — original human-readable reproducibility documentation.
- `back_matter/` — availability/declaration templates.
- `CITATION.cff` and `.zenodo.json` — current repository-release metadata.
- `PUBLIC_RELEASE_STATUS.json` — current two-layer release identity record.
- `MANIFEST_PUBLIC_RELEASE_v1.0.0.sha256` — preserved manifest for the original release.
- `MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256` — manifest generated after the v1.1.0 overlay is applied.
- `MANIFEST_PUBLIC_RELEASE.sha256` — current manifest alias; for v1.1.0 it should match `MANIFEST_PUBLIC_RELEASE_v1.1.0.sha256`.

## Data

The raw IGAR dataset is **not redistributed** in this repository.

Dataset:

- Mendeley Data, Version 3
- DOI: `10.17632/7zryc6k76z.3`
- License: CC BY 4.0
- Data article DOI: `10.1016/j.dib.2026.112708`

The released dataset-provided translation and VADER variables were analyzed as released; they were not silently regenerated for this study.

## Scientific interpretation guardrails

Neither weak-supervision source is treated as ground truth. The manuscript term is **weak-label disagreement**. The downstream RQ4 result is an association between disagreement and Transformer sensitivity to supervision-source choice, not a causal claim and not evidence that one weak-label source is superior.

Revision-stage diagnostics further show that class-specific target learnability and repeated-text structure contribute to the magnitude of the observed association. The primary coefficient is therefore not interpreted as a pure supervision-source identity effect independent of target structure.

## Verification

Verify the original canonical archive:

```bash
sha256sum canonical_archive/IGAR-Paper1-Reproducibility_STRICT_FINAL.zip
```

Expected:

```text
ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89
```

Verify the exact P1R-11 addendum ZIP:

```bash
sha256sum revision_addenda/IGAR_Paper1_P1R11_Reproducibility_Addendum_v0.6_CLOSED.zip
```

Expected:

```text
ce69cda9003425b7a5c326beb1531d27efb6149591416be32beee933dfd8356b
```

Verify the internal P1R-11 package:

```bash
cd revision_addenda/P1R11_v0.6_CLOSED
sha256sum -c manifests/SHA256SUMS.txt
python tools/verify_addendum.py
```

After applying the v1.1.0 overlay, repository-level verification is described in `MANIFEST_STRATEGY.md` and `GITHUB_ZENODO_RELEASE_GUIDE_v1.1.0.md`.

## License

Repository software and original release documentation are provided under the MIT License. The IGAR dataset is not included and retains its own CC BY 4.0 license.
