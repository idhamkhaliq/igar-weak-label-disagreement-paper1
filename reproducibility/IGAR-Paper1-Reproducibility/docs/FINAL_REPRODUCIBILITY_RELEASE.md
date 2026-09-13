# IGAR Paper 1 — Final Reproducibility Release

**Status:** `CLOSED / PASS — STRICT FORENSIC`

All four previously identified reproducibility gaps are closed.

## Closed gaps

1. Exact Cell 60A–60E training source archived.
2. Exact row_id and duplicate_group_id construction source archived.
3. Historical training and statistical environments attested and preserved.
4. Dataset and translation provenance documented and verified.

## Authoritative scientific environment

```text
Python        3.13.15
PyTorch       2.11.0+cu128
CUDA          12.8
GPU           Tesla T4
transformers  4.57.6
accelerate    1.14.0
tokenizers    0.22.2
safetensors   0.8.0
sentencepiece 0.2.2
NumPy         2.1.3
pandas        2.2.3
scikit-learn  1.6.1
statsmodels   0.15.0
```

## Scientific freeze

```text
Protocol ID             5b7ffaa036af
Overflow policy ID      61ec4762487c
RQ4 primary H4          SUPPORTED
Scientific recompute    False
Training rerun          False
New statistical tests   False
```

The release preserves the distinction between historical
scientific runtime provenance and later packaging runtime.

Neither weak-label source is treated as ground truth.
