# IGAR Paper 1 — Final Code Documentation

## Strict Forensic Reproducibility Record

**Paper:** *Characterizing Weak-Label Disagreement in Indonesian Government Application Reviews: A Large-Scale Empirical Study*  
**Release status:** **CLOSED / PASS — STRICT FORENSIC**  
**Scientific status:** **FINAL / FROZEN**  
**Manuscript status:** **CLEARED TO RESUME**

This document is the final code/reproducibility documentation record for Paper 1. It summarizes the frozen computational protocol, provenance, exact-source closure, environment capture, immutable hashes, and final release identifiers. It does **not** reopen the scientific analysis and does not introduce new statistical tests.

---

## 1. Final Release Identifiers

### Authoritative scientific source identity

The authoritative scientific source identity is defined at **component level**, not by the mutable byte-level hash of the whole Colab notebook.

```text
Scientific source component-set SHA256
bc5ec1a72c7168be6deba93036cb444748611f3a6e3735d47ffb9f479c779530
```

### Final package checksum manifest

```text
checksums_STRICT.sha256 SHA256
c1a594f0a9138e458345581dd5087977ce903e50bf28016161940ac57b6dfef2
```

### Final strict reproducibility ZIP

```text
IGAR-Paper1-Reproducibility_STRICT_FINAL.zip SHA256
ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89
```

The canonical ZIP has the same SHA256:

```text
IGAR-Paper1-Reproducibility.zip SHA256
ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89
```

ZIP CRC/integrity verification: **PASS**.

---

## 2. Notebook Provenance Reconciliation

The whole notebook changed at byte level during later reproducibility/packaging execution. This was explicitly reconciled rather than hidden.

```text
Notebook SHA at scientific-source extraction
b8cdc2ec148ca65dc90e5124776fcf05a385a4d930eb1fb0a245c1d1f059340f

Archived release notebook SHA
67dfc7eeeedc49dab757cef7a54dfc8757f8e8d7edbb96f23a361e7f29345e52
```

Full-notebook SHA drift was accepted only after exact scientific components were independently verified unchanged.

### Historical scientific-source boundary

The historical scientific source for `row_id` and `duplicate_group_id` is restricted to notebook cells **before Cell 60A**, i.e.:

```text
cell index < 63
```

Verified source locations:

```text
row_id construction                 : cell 26
duplicate_group_id construction     : cell 26
required historical dependencies    : cells 5, 25, 26
Cell 104                             : EXCLUDED / RESOLVED false positive
```

Cell 104 was a later reproducibility/packaging assignment detected by an earlier broad scanner and is **not** part of the historical scientific pipeline.

### Exact training-source archive

Cell 60A–60E were extracted using explicit marker boundaries and verified unchanged in the final release notebook.

```text
CELL 60A : PASS
CELL 60B : PASS
CELL 60C : PASS
CELL 60D : PASS
CELL 60E : PASS
```

Exact-source archive files in the release package include:

```text
src/08_train_paired_indobert_EXACT_EXTRACT.py
src/04_exact_row_duplicate_id_HISTORICAL_SOURCE.py
notebooks/Cell60A_60E_EXACT_SOURCE_ARCHIVE.json
notebooks/row_id_duplicate_group_id_EXACT_HISTORICAL_SOURCE_ARCHIVE.json
manifests/SCIENTIFIC_SOURCE_COMPONENTS_STRICT.json
```

---

## 3. Closure of the Four Reproducibility Gaps

All four originally identified gaps are closed.

| Gap | Final status | Closure basis |
|---|---|---|
| Exact Cell 60A–60E training source | CLOSED / PASS | Explicit marker-bounded exact extraction |
| Exact `row_id` / `duplicate_group_id` source | CLOSED / PASS | Historical assignment detection + helper dependencies |
| Exact environment provenance | CLOSED / PASS | Historical model stack locked; statistical stack attested; current runtime separated |
| Dataset / translation provenance | CLOSED / PASS | DOI/version/license + local data matches |

No scientific results were changed during closure.

```text
Scientific results changed   : False
Scientific results recomputed: False
Training rerun               : False
New statistical tests        : False
```

---

## 4. Dataset Provenance

**Dataset:** IGAR — Indonesian government applications review dataset for sentiment analysis  
**Mendeley Data DOI:** `10.17632/7zryc6k76z.3`  
**Version:** 3  
**License:** CC BY 4.0  
**Data article DOI:** `10.1016/j.dib.2026.112708`

Dataset files documented by the data article:

```text
Rating_labeled.csv
VADER_labeled.csv
```

The VADER file contains dataset-provided translation and VADER fields. Reproducibility therefore uses the frozen IGAR fields rather than silently regenerating translation through a contemporary translation API.

Local provenance verification found **2 matching local dataset files**.

### Raw dataset hash

```text
852c8b662224bd62418ef7b7dac15b9e43c9a6b4cdf0fef6239042203c2eccb0
```

---

## 5. Weak-Supervision Definitions

Neither supervision source is treated as ground truth.

### Rating-derived weak label

```text
1–2 stars -> Negative
3 stars   -> Neutral
4–5 stars -> Positive
```

### Translation-mediated VADER weak label

VADER is applied to the dataset-provided English translation field.

```text
compound <= -0.05          -> Negative
-0.05 < compound < 0.05    -> Neutral
compound >= 0.05           -> Positive
```

### Disagreement variable

```text
D = 0  if rating_label == vader_label
D = 1  otherwise
```

Preferred manuscript term: **weak-label disagreement**.

Do not substitute the following without direct evidence:

```text
label error
mislabelling
wrong label
ground-truth disagreement
```

### Severity coding

```text
Negative = -1
Neutral  =  0
Positive = +1

S = abs(code_rating - code_vader)
```

Thus:

```text
S = 0 : agreement
S = 1 : adjacent transition
S = 2 : opposite-polarity transition
```

Severity is a transition-distance descriptor, not evidence of true annotation-error severity.

---

## 6. Phase 1 — RQ1 / RQ2 Computational Record

Phase 1 ID:

```text
f11658d4e59a
```

Dataset size:

```text
N = 617,722
```

Frozen primary results:

```text
Agreement    = 362,308 = 58.652274%
Disagreement = 255,414 = 41.347726%
Cohen's kappa = 0.333802
```

3 x 3 rating-derived × VADER transition counts:

| Rating \ VADER | Negative | Neutral | Positive |
|---|---:|---:|---:|
| Negative | 100,703 | 85,653 | 60,542 |
| Neutral | 7,162 | 12,350 | 14,863 |
| Positive | 11,868 | 75,326 | 249,255 |

Disagreement severity:

```text
S1 = 183,004 = 71.65% of disagreements
S2 =  72,410 = 28.35% of disagreements
```

The structure is directional/asymmetric; this does not imply that either weak label is correct.

---

## 7. Phase 2 — Duplicate Groups / RQ3 Computational Record

Phase 2 ID:

```text
e02c73e14559
```

Deterministic identifiers:

- `row_id`: deterministic review-level identifier.
- `duplicate_group_id`: normalized within-application duplicate grouping.
- Normalization includes Unicode NFC plus trimming/collapsing whitespace.
- Missing text is kept unique.

Frozen duplicate statistics:

```text
Unique groups                   = 397,731
Exact full-row duplicates       = 38 rows / 19 extra rows
Normalized repeated groups      = 14,591
Rows in repeated groups         = 234,582 = 37.9753%
Maximum group size              = 7,429
```

Primary RQ3 dataset:

```text
N = 617,677
```

Primary model:

```text
disagreement ~
    C(score, Treatment(reference=5))
    + log_words
    + C(app, Treatment(reference='JMO'))
```

Cluster-robust inference is grouped by `duplicate_group_id`.

Frozen adjusted odds ratios include:

```text
1-star vs 5-star OR = 4.7407
2-star vs 5-star OR = 7.5460
3-star vs 5-star OR = 5.9156
4-star vs 5-star OR = 1.6319

log_words OR = 0.8779
95% CI       = [0.8158, 0.9447]
```

Year-adjusted application effects have confidence intervals including 1 and are therefore reported with temporal-instability qualification.

---

## 8. Gate 6A / Gate 6B — Model Protocol

### Model

```text
Checkpoint : indobenchmark/indobert-base-p1
Revision   : c2cd0b51ddce6580eb35263b39b0a1e5fb0a39e2
Hidden size: 768
Layers     : 12
Max pos.   : 512
```

### Historical scientific training environment

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
```

### Historical statistical stack

```text
NumPy         2.1.3
pandas        2.2.3
scikit-learn  1.6.1
statsmodels   0.15.0
```

### Current packaging/reference runtime

Later packaging used a newer model-stack runtime, including:

```text
transformers 5.16.1
tokenizers   0.23.1
```

These versions are documented as the later/current reference runtime and **do not replace** the historical training stack.

### Determinism

```text
attention implementation           : eager
torch deterministic algorithms     : True
warn_only                           : False
TF32                                : disabled
```

Gate/protocol identifiers:

```text
Gate 6A ID          : f4e14c6019ae
Final protocol ID   : 5b7ffaa036af
Overflow policy ID  : 61ec4762487c
```

---

## 9. Frozen RQ4 Cohort

Final cohort size:

```text
150,000 reviews
train = 105,000
validation = 22,500
test = 22,500
```

The frozen cohort must never be regenerated for the final Paper 1 analysis.

```text
Assignment SHA256
bce0a04a9781ffe05a580c5af83d937a0df93e023bcdbac82de04d205b36a7e1

Frozen cohort SHA256
ba13d30077a39e5aaacd6058c07454e31b0d938ebc949ce09edea7bc5a235912

Tokenized cohort SHA256
e99c92c57ae28350c268a51a9cef66f9f44ade95a36d2fc61947ed5ff8ce6272
```

### Training configuration

```text
max length             : 128
dynamic padding        : yes
physical batch size    : 16
gradient accumulation  : 2
effective batch size   : 32
mixed precision        : FP16
learning rate          : 2e-5
weight decay            : 0.01
warmup                  : 10%
epochs                  : 2 fixed
seeds                   : [42, 123, 2026]
early stopping          : no
inference batch         : 64
inference chunk         : 5000
```

Within each seed, Model-R and Model-V use identical classifier initialization and identical sample order. The only intended experimental difference is the supervision target.

```text
Model-R target : rating-derived weak label
Model-V target : translation-mediated VADER weak label
```

---

## 10. Final Model Artifact Hashes

```text
Seed 42  Model-R
78daac294df3438bba72a1eeb35024c543ffc9e7aa78a643f144c431bf823c99

Seed 42  Model-V
5472a992eb75acc5eaede24254c601679151d3eb4b9a1423fc67c80a1c5c3a90

Seed 123 Model-R
53da37dcbd5ca2ada3d707890c9d839e93b9133c2d684bbad3bccd8a2e5d4c84

Seed 123 Model-V
7be38e2def25d35408024f3156f0c662614657d527d02241882b30c5e2472e88

Seed 2026 Model-R
130d4bdc1e77312b4d65fb2719791121f07a00a4fb47602fe307aa2577864754

Seed 2026 Model-V
92ed977edc8b977e291a8707d2a1aa85781ad68f0746c7c7522b18278855b86c
```

All six final model artifacts passed integrity verification. Four artifacts that had become unavailable because of Drive/FUSE loss were reproduced byte-for-byte using the frozen deterministic engine.

---

## 11. Final Test Probability Hashes

Canonical test-row order:

```text
ee4efe4d3f5e620c36f56923e4ab3481a65cdace75fae984b44cab009a508ded
```

Probability artifacts:

```text
42 R   7c16acbf2547f09ec2c1d58406b541254e94375e63269126f75edb0fab7f7a05
42 V   537ee8517e58f9e07891440c7545fc7c983c87354311c9457855b922d53237a5
123 R  95853e41f906e1e2de17e308b59ebf4957f59b4a1eced265356f378a0614075f
123 V  6646d4f9c0fa1022b7f5fe7eef483a79a3e92bdb3e8018d51cdda83c05c40226
2026 R 7b5d0ddbc75c08301d4eb4f0a7eae6e4c27190d11515ebcc18676a41f8e22278
2026 V 4b550ae12fbddf380a41ac38a5b6e5e918c3ebc19c75e87e1a5dcd94ee38f7c3
```

---

## 12. JSD Construction

Primary RQ4 outcome is Jensen-Shannon divergence using natural logarithms.

For paired prediction distributions `P_R` and `P_V`:

```text
M = 0.5 * (P_R + P_V)

JSD(P_R, P_V)
= 0.5 * KL(P_R || M)
+ 0.5 * KL(P_V || M)
```

Range under natural logarithms:

```text
0 <= JSD <= ln(2)
```

The primary review-level outcome is the mean JSD across the three paired seeds.

Frozen hashes:

```text
Three-seed JSD matrix SHA256
40cbe58d590b34bc1279b56b325156cc9f10a8a75fc6eb316ed8894facfee2c1

Mean-seed JSD SHA256
2688ce3f06ad8eb5f16bfc52b5f3185372838f92ed983f9afc334154cb739903
```

---

## 13. Primary H4 Statistical Code Path

Primary analysis unit: **review**, not seed × review.

Conceptual model:

```text
mean_seed_JSD ~ disagreement
```

Estimator:

```text
OLS
cluster-robust standard errors by duplicate_group_id
use_t inference
```

Frozen primary result:

```text
N reviews       = 22,500
Clusters        = 15,921
Agreement N     = 13,196
Disagreement N  = 9,304

Agreement mean JSD    = 0.05190023
Disagreement mean JSD = 0.40646891

Beta = 0.3545686801
SE   = 0.00610784
t    = 58.05144
95% CI = [0.34259663, 0.36654073]
p < .001
```

H4 status: **SUPPORTED**.

Permitted interpretation:

> Weak-label disagreement is associated with greater Transformer prediction sensitivity to the choice of weak-supervision source.

Not permitted:

```text
weak-label disagreement causes divergence
one weak label is the correct label
the higher within-source F1 identifies the superior label source
```

---

## 14. Frozen Sensitivity / Exploratory Analyses

### Large duplicate-cluster sensitivity

```text
Primary beta       = 0.354569
Exclude largest 1  = 0.355058
Exclude largest 5  = 0.348804
Exclude largest 10 = 0.347277
Maximum absolute beta change = 2.056%
```

All confidence intervals remained positive.

### Severity exploration

```text
S0 mean JSD = 0.051900
S1 mean JSD = 0.440888
S2 mean JSD = 0.319494
```

Observed ordering:

```text
S0 < S2 < S1
```

This is explicitly **non-monotonic** and should be interpreted as directional transition composition rather than increasing label-error severity.

### Application-level descriptive heterogeneity

The disagreement-minus-agreement JSD direction was positive in all six applications. Application results are descriptive; BMKG and KAI test subsets are small and require caution.

### Secondary hard-prediction diagnostic

```text
Agreement reviews    : hard R-vs-V disagreement = 9.15%
Disagreement reviews : hard R-vs-V disagreement = 79.99%
```

JSD remains the primary outcome because it retains probability-distribution information beyond argmax disagreement.

---

## 15. Paper-Ready Scientific Artifacts

Paper-ready root in the author's project:

```text
/content/drive/MyDrive/IGAR_Paper1/paper_ready
```

Main scientific architecture:

```text
Table 1  RQ1 overall/application-specific weak-label agreement
Table 2  RQ1/RQ2 directional transition structure
Table 3  RQ3 adjusted associations
Table 4  RQ4 primary disagreement–JSD association

Figure 1 Study framework
Figure 2 Weak-label transition structure
Figure 3 Star/application disagreement structure
Figure 4 RQ3 adjusted OR forest
Figure 5 RQ4 review-level JSD distribution
```

Tables 1–4: **FINAL / LOCKED**  
Figures 1–5: **FINAL / LOCKED**

No scientific recomputation is permitted during manuscript formatting/packaging.

---

## 16. Final Reproducibility Package Structure

The final package is named:

```text
IGAR-Paper1-Reproducibility
```

Core release contents include:

```text
README.md
config/
docs/
environment/
manifests/
notebooks/
src/
tools/
outputs/
```

Strict forensic release-critical files include:

```text
manifests/REPRODUCIBILITY_STATUS_STRICT.json
manifests/SCIENTIFIC_SOURCE_COMPONENTS_STRICT.json
manifests/checksums_STRICT.sha256

docs/NOTEBOOK_PROVENANCE_RECONCILIATION.md
docs/FINAL_REPRODUCIBILITY_RELEASE.md

environment/environment_provenance_STRICT.json
environment/requirements-HISTORICAL-TRAINING.txt
environment/requirements-REFERENCE-STATISTICAL-REPRODUCTION.txt
environment/pip-freeze-CURRENT-REFERENCE-RUNTIME.txt

src/08_train_paired_indobert_EXACT_EXTRACT.py
src/04_exact_row_duplicate_id_HISTORICAL_SOURCE.py

notebooks/Paper1_Phase1_RUN_FINAL_ARCHIVE.ipynb
notebooks/Cell60A_60E_EXACT_SOURCE_ARCHIVE.json
notebooks/row_id_duplicate_group_id_EXACT_HISTORICAL_SOURCE_ARCHIVE.json
```

---

## 17. Verification Commands for the Final Archive

Verify ZIP checksum:

```bash
sha256sum IGAR-Paper1-Reproducibility_STRICT_FINAL.zip
```

Expected:

```text
ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89
```

Verify ZIP integrity with Python:

```python
import zipfile

path = "IGAR-Paper1-Reproducibility_STRICT_FINAL.zip"

with zipfile.ZipFile(path, "r") as zf:
    bad = zf.testzip()
    assert bad is None

print("ZIP integrity: PASS")
```

Verify package file checksums after extraction:

```bash
cd IGAR-Paper1-Reproducibility
sha256sum -c manifests/checksums_STRICT.sha256
```

---

## 18. Scientific Freeze Rules

From this release onward:

1. Do not regenerate the 150k RQ4 cohort.
2. Do not retrain Model-R or Model-V for Paper 1 unless a genuine reproducibility defect is discovered.
3. Do not add post hoc hypothesis tests to frozen RQ4 results.
4. Do not reinterpret translation-mediated VADER or rating-derived labels as ground truth.
5. Do not rank weak-label sources by cross-supervision F1.
6. Do not replace the historical training environment with the later packaging environment.
7. Do not use whole-notebook SHA as the sole scientific-source identity; use the locked component-set SHA.
8. Manuscript values must be taken from the frozen paper-ready tables/source map rather than recomputed ad hoc.

---

## 19. Final Closure Statement

```text
REPRODUCIBILITY RELEASE : CLOSED / PASS — STRICT FORENSIC
NOTEBOOK SHA DRIFT      : RECONCILED
CELL 104 FALSE POSITIVE : RESOLVED
SCIENTIFIC SOURCE CODE  : COMPONENT-HASH VERIFIED
FOUR ORIGINAL GAPS      : CLOSED
PAPER 1 SCIENCE         : FINAL / FROZEN
TABLES 1–4              : FINAL / LOCKED
FIGURES 1–5             : FINAL / LOCKED
MANUSCRIPT WRITING      : CLEARED TO RESUME
```

### Authoritative release identifiers

```text
Scientific source component-set SHA256
bc5ec1a72c7168be6deba93036cb444748611f3a6e3735d47ffb9f479c779530

Package checksum-manifest SHA256
c1a594f0a9138e458345581dd5087977ce903e50bf28016161940ac57b6dfef2

Final strict ZIP SHA256
ae8eb3d4400e32ae52a7b6526420bd8421f36af1f5d27a576cb56119e7c96d89
```

---

**Document role:** final human-readable code/reproducibility documentation record.  
**Scientific computation performed while creating this document:** none.  
**Scientific results modified:** none.
