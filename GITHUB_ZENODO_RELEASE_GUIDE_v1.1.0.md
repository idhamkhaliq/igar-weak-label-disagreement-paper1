> **Historical/completed workflow record.** GitHub release v1.1.0 has already been published. This file is retained for provenance and must not be interpreted as current release instructions or as the preferred terminology of the final resubmission manuscript. Do not re-run these publication steps or retag v1.1.0.

# GitHub + Zenodo publication guide — v1.1.0

This file records the completed workflow that produced the published v1.1.0 reproducibility release.

## Historical release identity

Audited v1.0.0 baseline commit:

`795a5e187e5aef15f856d02ca01ce42e1e68e319`

Published v1.1.0 release commit:

`6d4e3bebbc8d958e2785268ccaa3613a7824b339`

Original canonical archive SHA-256:

`ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89`

Exact versioned post hoc addendum ZIP SHA-256:

`ce69cda9003425b7a5c326beb1531d27efb6149591416be32beee933dfd8356b`

Historical internal addendum path:

`revision_addenda/P1R11_v0.6_CLOSED/`

The internal identifier `P1R-11` is retained for traceability. In the final resubmission manuscript and current public narrative, the corresponding work is described as a **versioned reproducibility addendum for post hoc sensitivity and diagnostic analyses**.

## Current interpretation

Release v1.1.0 is the reproducibility companion for the final manuscript resubmission. The original analytic samples, trained models, test predictions, and primary RQ1–RQ4 estimates remain unchanged. The later analyses use preserved predictions and metadata and do not introduce retraining, a new architecture, an additional weak-supervision source, new data collection, or changes to the frozen cohort or splits.

Neither weak-supervision source is treated as ground truth, and the analyses are not used to rank source correctness.

## Historical safety rules

- Do not force-push historical release tags.
- Do not delete or retag `v1.0.0` or `v1.1.0`.
- Do not rewrite the historical `v1.0.0` release as if the later post hoc analyses were part of the original analysis execution.
- Do not change files inside `canonical_archive/`.
- Do not merge the post hoc addendum into the original frozen `reproducibility/` tree.
- Do not upload raw IGAR data or preserved probability inputs as public data unless separately intended and licensed.
