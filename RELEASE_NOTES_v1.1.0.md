# IGAR Paper 1 Reproducibility Package v1.1.0 — P1R-11 Revision Addendum

Version **1.1.0** is an additive reproducibility release for the revised manuscript:

**Characterizing Weak-Label Disagreement in Indonesian Digital Public-Service Application Reviews: Transformer Sensitivity to Supervision-Source Choice**

## What is new

This release adds the closed **P1R-11 revision-stage reproducibility addendum** under:

`revision_addenda/P1R11_v0.6_CLOSED/`

The addendum archives:

- the canonical reconstruction/closure script;
- machine-readable reproduced results;
- the 33-target validation report;
- probability-integrity and provenance records;
- source tables supporting Supplementary Tables S11–S14;
- canonical closure-run environment capture;
- historical execution recovery records;
- final cross-document numerical audit records;
- exact SHA-256 manifests and closure verification.

Closure status:

- **15/15 blocking checks PASS**
- **33/33 numerical targets PASS**
- P1R-11 internal status: **CLOSED**

Exact P1R-11 package ZIP SHA-256:

`ce69cda9003425b7a5c326beb1531d27efb6149591416be32beee933dfd8356b`

## What is unchanged

Release v1.1.0 does **not** replace the original frozen release.

The original v1.0.0 computational record remains separately identifiable, including its canonical strict archive:

`ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89`

The original analytic samples, trained models, test predictions, and primary RQ1–RQ4 estimates were retained unchanged. P1R-11 did not introduce model retraining, a new architecture, an additional weak-supervision source, new data collection, or changes to the frozen cohort or train/validation/test assignments.

## Interpretation boundary

The revision-stage analyses are sensitivity and diagnostic analyses. Neither weak-supervision source is treated as ground truth, and the results are not used to rank source correctness. The primary RQ4 coefficient is not interpreted as a pure supervision-source identity effect independent of target structure.

## Data

The raw IGAR dataset is not redistributed here. It remains available from Mendeley Data, Version 3, DOI `10.17632/7zryc6k76z.3`, under CC BY 4.0.

## Verification

The repository contains both a browseable copy and the exact closed addendum ZIP. See `README.md`, `MANIFEST_STRATEGY.md`, and `revision_addenda/P1R11_v0.6_CLOSED/manifests/` for verification instructions.
