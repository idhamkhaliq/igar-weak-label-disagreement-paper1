# IGAR Paper 1 — Public Reproducibility Release v1.0.0

Reproducibility materials for:

**Characterizing Weak-Label Disagreement in Indonesian Digital Public-Service Application Reviews: Transformer Sensitivity to Supervision-Source Choice**

Authors:

- **Idham Khaliq**, Master's Program in Informatics, Faculty of Industrial Technology, Universitas Ahmad Dahlan — ORCID: 0009-0004-5214-5583
- **Uturestantix**, Department of Management, Faculty of Economics and Business, Universitas Cenderawasih — ORCID: 0000-0001-8321-8731

## Release status

This repository package contains the **authoritative strict-forensic reproducibility archive** for Paper 1.

- Reproducibility release: **CLOSED / PASS — STRICT FORENSIC**
- Scientific status: **FINAL / FROZEN**
- Canonical strict ZIP SHA256: `ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89`
- Scientific source component-set SHA256: `bc5ec1a72c7168be6deba93036cb444748611f3a6e3735d47ffb9f479c779530`
- Canonical checksum-manifest SHA256: `c1a594f0a9138e458345581dd5087977ce903e50bf28016161940ac57b6dfef2`

No scientific results were recomputed, no training was rerun, and no new statistical tests were performed while preparing this public release.

## Structure

- `canonical_archive/` — immutable strict-final ZIP and its SHA256 sidecar.
- `reproducibility/IGAR-Paper1-Reproducibility/` — exact extracted contents of the strict-final archive.
- `docs/` — final human-readable strict-forensic documentation.
- `back_matter/` — manuscript-facing availability and declaration templates.
- `CITATION.cff` and `.zenodo.json` — software citation / Zenodo metadata.
- `PUBLIC_RELEASE_STATUS.json` — public-release identity record.

## Data

The raw IGAR dataset is **not redistributed** in this repository.

Dataset:
- Mendeley Data, Version 3
- DOI: `10.17632/7zryc6k76z.3`
- License: CC BY 4.0
- Data article DOI: `10.1016/j.dib.2026.112708`

The released dataset-provided translation and VADER variables were used as released; they were not silently regenerated.

## Scientific interpretation guardrail

Neither weak-supervision source is treated as ground truth. The manuscript term is **weak-label disagreement**. The downstream RQ4 result is an association between disagreement and Transformer sensitivity to supervision-source choice, not a causal claim and not evidence that one weak-label source is superior.

## Verification

Verify the canonical archive:

```bash
sha256sum canonical_archive/IGAR-Paper1-Reproducibility_STRICT_FINAL.zip
```

Expected:

```text
ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89
```

The archive's internal file checksums are recorded in:

`reproducibility/IGAR-Paper1-Reproducibility/manifests/checksums_STRICT.sha256`

## License

Repository software and original release documentation are provided under the MIT License. The IGAR dataset is not included and retains its own CC BY 4.0 license.

## GitHub / Zenodo

Before the first GitHub release:
1. Replace the GitHub username placeholder in `CITATION.cff`.
2. Create a public GitHub repository, recommended name: `igar-weak-label-disagreement-paper1`.
3. Connect that repository to Zenodo.
4. Create GitHub Release `v1.0.0`.
5. Record the resulting Zenodo DOI in the manuscript Code availability statement.
