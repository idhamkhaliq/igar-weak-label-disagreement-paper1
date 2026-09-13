# IGAR Paper 1 Reproducibility Package

Reproducibility package for:

**Characterizing Weak-Label Disagreement in Indonesian Government Application Reviews: A Large-Scale Empirical Study**

## Status

This package is **scientifically frozen**. The included `tools/colab_close_gaps.py` must be run once in the author's final Google Colab/Drive environment to capture four pieces of exact provenance that cannot be inferred safely from result artifacts alone:

1. verbatim final Cell 60A–60E training source;
2. verbatim `row_id` / `duplicate_group_id` construction code;
3. exact NumPy/pandas/scikit-learn/statsmodels versions plus full `pip freeze`;
4. local raw-data acquisition/provenance record, combined with the public Mendeley V3 metadata already included here.

The finalizer refuses to mark the release `CLOSED` unless the exact-source checks succeed.

## Public dataset provenance

IGAR is published as Mendeley Data **Version 3**, DOI `10.17632/7zryc6k76z.3`, with CC BY 4.0 licensing. The data article documents two repository files, `Rating_labeled.csv` and `VADER_labeled.csv`; the latter includes translation and VADER-derived fields. See `config/data_provenance.json`.

## Reproduction order

1. Verify raw data SHA-256.
2. Reproduce/verify weak labels and RQ1–RQ2.
3. Reproduce deterministic row/group identifiers and RQ3.
4. Verify the frozen 150k RQ4 cohort and tokenized-cohort hashes.
5. Train paired Model-R / Model-V under the frozen deterministic protocol.
6. Verify six model hashes.
7. Perform blind test inference and verify six probability hashes plus test-row-order hash.
8. Compute natural-log JSD and verify JSD hashes.
9. Run the locked primary H4 model.
10. Run only the frozen sensitivity/exploratory diagnostics.
11. Generate tables/figures only from frozen sources.

## Finalizer

In the final Colab runtime, copy/unzip this folder to:

`/content/drive/MyDrive/IGAR-Paper1-Reproducibility`

Then run:

```bash
python /content/drive/MyDrive/IGAR-Paper1-Reproducibility/tools/colab_close_gaps.py \
  --package-root /content/drive/MyDrive/IGAR-Paper1-Reproducibility \
  --project-root /content/drive/MyDrive/IGAR_Paper1
```

Finally verify:

```bash
python /content/drive/MyDrive/IGAR-Paper1-Reproducibility/tools/verify_release.py \
  --package-root /content/drive/MyDrive/IGAR-Paper1-Reproducibility
```

A successful finalization writes `manifests/REPRODUCIBILITY_STATUS.json` with `status = CLOSED`.

## Scientific interpretation lock

Use **weak-label disagreement**. Neither rating-derived nor translation-mediated VADER labels are treated as ground truth. Model-R vs Model-V F1 values are within-supervision diagnostics and must not be used to rank supervision-source correctness.
