# IGAR Paper 1 Reproducibility Package v1.1.0 — Final-Resubmission Companion

Version **1.1.0** is the reproducibility release accompanying the final resubmission of:

**Characterizing Weak-Label Disagreement in Indonesian Digital Public-Service Application Reviews: Transformer Sensitivity to Supervision-Source Choice**

## What v1.1.0 adds

Release v1.1.0 preserves the original frozen v1.0.0 computational record and adds a separate, versioned **post hoc reproducibility addendum** based on preserved RQ4 test predictions and associated metadata.

The addendum was developed under the historical internal workflow identifier **P1R-11**, which is retained in archive paths and filenames for traceability. In the final manuscript and current public narrative, these analyses are described as **post hoc sensitivity and diagnostic analyses**.

The addendum archives:

- the reconstructed closure/reproduction script;
- machine-readable reproduced results;
- the 33-target validation report;
- probability-integrity and provenance records;
- source tables supporting Supplementary Tables S11–S14;
- canonical closure-run environment capture;
- historical execution recovery records;
- exact SHA-256 manifests and closure verification.

Closure status:

- **15/15 blocking checks PASS**
- **33/33 numerical targets PASS**
- internal addendum status: **CLOSED**

Exact addendum package ZIP SHA-256:

`ce69cda9003425b7a5c326beb1531d27efb6149591416be32beee933dfd8356b`

## What is unchanged

Release v1.1.0 does **not** replace or rewrite the original frozen release.

The original v1.0.0 computational record remains separately identifiable, including its canonical strict archive:

`ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89`

The original analytic samples, trained models, test predictions, and primary RQ1–RQ4 estimates were retained unchanged. The post hoc analyses did not introduce model retraining, a new architecture, an additional weak-supervision source, new data collection, or changes to the frozen cohort or train/validation/test assignments.

Historical `new_statistical_tests: false` statements in the v1.0.0 layer apply only to that original frozen analysis layer and must not be interpreted as denying the later post hoc analyses documented in v1.1.0.

## Interpretation boundary

Neither weak-supervision source is treated as ground truth, and the results are not used to rank source correctness.

The primary RQ4 association is not interpreted as a pure causal source-identity effect. Post hoc diagnostics indicate that the magnitude and heterogeneity of the observed association are sensitive to weak-label class composition and repeated-text structure, while within-supervision performance is interpreted as a learnability diagnostic rather than evidence of source correctness.

Singleton sensitivity is defined using the duplicate mapping of the **full usable-text source corpus**, not uniqueness within the RQ4 test set.

## Final-resubmission alignment

The current public-facing narrative uses the terminology and interpretation boundaries of the final resubmission manuscript. Historical internal identifiers remain preserved only where required for provenance.

This narrative alignment does not alter the frozen computational artifacts, machine outputs, source tables, or cryptographic identities of the v1.0.0 and v1.1.0 reproducibility layers.

## Data

The raw IGAR dataset is not redistributed here. It remains available from Mendeley Data, Version 3, DOI `10.17632/7zryc6k76z.3`, under CC BY 4.0.
