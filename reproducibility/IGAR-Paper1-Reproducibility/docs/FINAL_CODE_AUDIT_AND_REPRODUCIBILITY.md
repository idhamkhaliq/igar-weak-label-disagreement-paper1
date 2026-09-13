# IGAR Paper 1 — Final Code Audit and Reproducibility Specification

**Paper title:** *Characterizing Weak-Label Disagreement in Indonesian Government Application Reviews: A Large-Scale Empirical Study*  
**Scope:** Final code/protocol audit for RQ1–RQ4 and paper-ready artifact generation  
**Study status:** Scientific analyses frozen; main tables and Figures 1–5 locked  
**Final RQ4 protocol ID:** `5b7ffaa036af`  
**Overflow engineering policy ID:** `61ec4762487c`

---

## 1. Purpose of this document

This file records the **final implementation choices actually used** in Paper 1 so that another researcher can reconstruct the analysis with minimal ambiguity.

It is intended to:
1. distinguish authoritative final code from superseded/debug cells;
2. record frozen analysis choices, seeds, model configuration, hashes, and decision rules;
3. document implementation incidents relevant to reproducibility;
4. identify source-packaging gaps that still need to be closed before public release.

No scientific result is changed by this audit.

---

## 2. Audit verdict

**Scientific reproducibility status: PASS WITH ONE RELEASE-PACKAGING GAP**

The statistical design, frozen cohort, model hashes, inference hashes, JSD hashes, H4 decision rule, robustness checks, secondary analyses, and manuscript source maps are internally consistent and locked.

The main remaining gap is **source-code packaging**: the full exact training engine used in final Cell 60A and its run cells must be exported from the original Colab notebook/script into the public repository. The present audit records the frozen training specification and all final hashes, but not the complete original training-loop source text.

Therefore:

- **analysis integrity:** PASS
- **result provenance:** PASS
- **model provenance:** PASS
- **final statistical code path:** PASS
- **public release readiness:** CONDITIONAL on exporting the exact training source and complete environment lock

---

# 3. Terminology and interpretation lock

## 3.1 Preferred term

Use:

> **weak-label disagreement**

Do not automatically call disagreement:

- label noise
- mislabeled samples
- annotation errors
- incorrect labels
- ground-truth errors

The two weak-supervision sources are treated as alternative inexpensive supervision signals, not as ground truth.

## 3.2 Weak-label sources

### Rating-derived weak label

```text
1–2 stars -> Negative
3 stars   -> Neutral
4–5 stars -> Positive
```

### Translation-mediated VADER weak label

```text
compound <= -0.05         -> Negative
-0.05 < compound < 0.05  -> Neutral
compound >= 0.05          -> Positive
```

Preferred manuscript term:

> **translation-mediated VADER weak label**

---

# 4. Dataset provenance and integrity locks

## 4.1 Dataset

IGAR Indonesian government-application review dataset.

Applications:

```text
BMKG
JMO
KAI
Mobile JKN
MyPertamina
SATUSEHAT
```

Total rows:

```text
617,722
```

Dataset SHA256:

```text
852c8b662224bd62418ef7b7dac15b9e43c9a6b4cdf0fef6239042203c2eccb0
```

Phase 1 ID:

```text
f11658d4e59a
```

## 4.2 Missing-value audit

```text
content missing       : 26
appVersion missing    : 90,403
translation missing   : 7,775
```

---

# 5. Locked research questions

## RQ1
To what extent do the rating-derived and translation-mediated VADER weak labels agree?

## RQ2
How is weak-label disagreement structured across directional transitions, severity, star ratings, and applications?

## RQ3
Which observable review characteristics are associated with weak-label disagreement?

## RQ4
To what extent is weak-label disagreement associated with sensitivity of Transformer predictions to the choice of weak-supervision source?

Conceptual sequence:

```text
Characterize -> Explain/structure -> Measure ML sensitivity
```

---

# 6. Phase 1 — RQ1 and RQ2 final specification

## 6.1 Core disagreement definition

```python
CLASS_CODE = {
    "Negative": -1,
    "Neutral":   0,
    "Positive":  1,
}

disagreement = (rating_label != vader_label).astype(int)

severity = abs(
    rating_label.map(CLASS_CODE)
    - vader_label.map(CLASS_CODE)
)
```

Interpretation:

```text
S=0 -> agreement
S=1 -> adjacent disagreement
S=2 -> extreme Negative <-> Positive disagreement
```

## 6.2 Frozen RQ1 totals

```text
Agreement     : 362,308 / 617,722 = 58.652274%
Disagreement  : 255,414 / 617,722 = 41.347726%
Cohen's kappa : 0.333802
```

## 6.3 Frozen 3x3 transition counts

Rows = rating-derived weak label.  
Columns = translation-mediated VADER weak label.

```text
                    VADER Neg   VADER Neu   VADER Pos
Rating Negative       100,703      85,653      60,542
Rating Neutral          7,162      12,350      14,863
Rating Positive        11,868      75,326     249,255
```

## 6.4 Frozen severity totals

```text
Severity 1 : 183,004
Severity 2 : 72,410
```

Among disagreements:

```text
Severity 1 : 71.65%
Severity 2 : 28.35%
```

## 6.5 Star-rating disagreement percentages

```text
1 star : 57.909559%
2 star : 68.656268%
3 star : 64.072727%
4 star : 34.361749%
5 star : 24.602550%
```

## 6.6 RQ2 structural association checks

```text
app x disagreement      Cramér's V = 0.1351
score x disagreement    Cramér's V = 0.3499
app x severity          Cramér's V = 0.09685
score x severity        Cramér's V = 0.3038
```

All: `p < .001`.

Interpretation lock:

> Star rating showed the stronger structural association. Application effects were smaller.

---

# 7. Phase 2 — text normalization, duplicate structure, and RQ3

Phase 2 ID:

```text
e02c73e14559
```

## 7.1 Duplicate-group definition

Normalized duplicate groups used:

```text
same application
+
NFC Unicode normalization
+
trim leading/trailing whitespace
+
collapse repeated whitespace
+
normalized review content
```

Missing review content was treated as unique.

Conceptual normalization:

```python
import re
import unicodedata

def normalize_review_text(x):
    if x is None:
        return None
    x = unicodedata.normalize("NFC", str(x))
    x = re.sub(r"\s+", " ", x.strip())
    return x
```

The exact `row_id` and `duplicate_group_id` hashing functions must be exported verbatim from the original notebook for byte-identical public replication.

## 7.2 Duplicate audit

```text
Unique normalized groups      : 397,731
Exact full-row duplicates     : 38 rows / 19 extra rows
Repeated normalized groups    : 14,591
Rows in repeated groups       : 234,582 (37.9753%)
Maximum duplicate-group size  : 7,429
```

Repeated texts were retained in the primary RQ3 analysis.

Only the 19 extra exact full-row duplicates were excluded from the final primary RQ3 dataset.

Primary source:

```text
/content/drive/MyDrive/IGAR_Paper1/phase2/data/05_RQ3_primary_final.parquet
```

Primary N:

```text
617,677
```

## 7.3 Review length

```python
log_words = np.log1p(n_words)
```

Frozen word-count summary:

```text
mean   8.42
median 4
p90    22
p95    31
p99    55
max    283
```

## 7.4 Primary RQ3 model

Locked formula:

```python
disagreement ~ C(score, Treatment(reference=5))              + log_words              + C(app, Treatment(reference='JMO'))
```

Inference:

```text
Logistic regression
Cluster-robust SE by duplicate_group_id
```

`appVersion` was excluded.

## 7.5 Frozen primary adjusted odds ratios

```text
1 star vs 5 stars         OR 4.7407   95% CI 4.1878–5.3666
2 stars vs 5 stars        OR 7.5460   95% CI 6.6619–8.5474
3 stars vs 5 stars        OR 5.9156   95% CI 4.9260–7.1041
4 stars vs 5 stars        OR 1.6319   95% CI 1.5390–1.7303

BMKG vs JMO               OR 1.9750   95% CI 1.4317–2.7244
KAI vs JMO                OR 1.3976   95% CI 1.1459–1.7046
Mobile JKN vs JMO         OR 1.1691   95% CI 0.9075–1.5061
MyPertamina vs JMO        OR 1.0817   95% CI 0.8954–1.3069
SATUSEHAT vs JMO          OR 1.2724   95% CI 0.9880–1.6387

log_words                  OR 0.8779   95% CI 0.8158–0.9447
```

Equivalent effect for doubling review length:

```text
OR = 0.9137
95% CI = 0.8684–0.9613
```

McFadden pseudo-R²:

```text
0.0952
```

## 7.6 RQ3 sensitivity analyses

```text
Primary:
repeated normalized review groups retained
cluster-robust SE by duplicate_group_id

Sensitivity 1:
singleton-only
HC1 robust SE

Sensitivity 2:
year-adjusted
cluster-robust SE
```

Interpretation lock:

> Application associations were not temporally stable after review-year adjustment; year-adjusted application confidence intervals included 1.

---

# 8. Phase 3 Gate 6A — model and tokenizer audit

Gate 6A ID:

```text
f4e14c6019ae
```

Environment observed:

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

Checkpoint:

```text
indobenchmark/indobert-base-p1
```

Revision:

```text
c2cd0b51ddce6580eb35263b39b0a1e5fb0a39e2
```

Architecture:

```text
hidden size 768
12 Transformer layers
maximum position embeddings 512
```

## 8.1 Token-length audit

```text
N        617,696
p50      7
p75      16
p90      31
p95      43
p99      74
p99.5    89
p99.9    111
max      498
<=128    99.9707%
>128     181 rows
```

Locked maximum sequence length:

```text
128 tokens
```

## 8.2 Tokenizer-class audit note

Gate 6A originally reported:

```text
BertTokenizerFast
```

During blind-test inference the runtime reported:

```text
BertTokenizer
```

This did not change the locked revision, row order, probability hashes, or final results. For public release, explicitly instantiate and document the tokenizer class/`use_fast` setting used by the released script.

---

# 9. Gate 5B — frozen RQ4 cohort

**Never regenerate this cohort when the frozen artifact is available.**

Frozen cohort:

```text
/content/drive/MyDrive/IGAR_Paper1/phase3/gate5b/data/IGAR_RQ4_Final_Cohort_150k.parquet
```

Cohort SHA256:

```text
ba13d30077a39e5aaacd6058c07454e31b0d938ebc949ce09edea7bc5a235912
```

Assignment SHA256:

```text
bce0a04a9781ffe05a580c5af83d937a0df93e023bcdbac82de04d205b36a7e1
```

Gate 5B ID:

```text
9bfb0c825768
```

Frozen cohort:

```text
Eligible rows      : 617,677
Cohort             : 150,000
Train              : 105,000
Validation         : 22,500
Test               : 22,500
Selected groups    : 103,261
Leakage            : none
Overall strata     : 54
Split-cell coverage: 161/161
```

Seeds:

```text
split seed      = 1175
selection seed  = 52026
```

Token overflow:

```text
>128 tokens = 43 / 150,000 = 0.0287%
```

---

# 10. Gate 6B — deterministic training protocol

Tokenized cohort SHA256:

```text
e99c92c57ae28350c268a51a9cef66f9f44ade95a36d2fc61947ed5ff8ce6272
```

Final protocol ID:

```text
5b7ffaa036af
```

Strict determinism:

```text
attention implementation: eager
deterministic algorithms: True
warn_only: False
TF32: disabled
```

Core setup:

```python
torch.use_deterministic_algorithms(True, warn_only=False)
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False
```

Training configuration:

```text
model checkpoint        indobenchmark/indobert-base-p1
revision                c2cd0b51ddce6580eb35263b39b0a1e5fb0a39e2
max_length              128
dynamic padding         yes
physical batch size     16
gradient accumulation   2
effective batch size    32
mixed precision         FP16
learning rate           2e-5
weight decay            0.01
warmup                   10%
epochs                   2 fixed
early stopping           no
seeds                    42, 123, 2026
inference batch size     64
inference chunk size     5000
```

Paired design:

```text
Model-R target = rating_target
Model-V target = vader_target
```

Training class IDs:

```python
LABEL_TO_ID = {
    "Negative": 0,
    "Neutral":  1,
    "Positive": 2,
}
```

Within each seed:

- Model-R and Model-V start from the same classifier initialization.
- They use the same epoch-specific sample order.
- Architecture/configuration is identical.
- Only the supervision target changes.
- Validation is diagnostic only.
- Test remains untouched until final blind inference.

Checkpoints retained around:

```text
2000
4000
6000 optimizer steps
```

---

# 11. FP16 overflow and exact run completion

Every final run completed:

```text
6,564 successful optimizer updates
210,000 training examples
one FP16 overflow event
```

Overflow steps:

```text
seed 42   Model-R : 6015
seed 42   Model-V : 6429
seed 123  Model-R : 6005
seed 123  Model-V : 6564
seed 2026 Model-R : 6171
seed 2026 Model-V : 6280
```

Seed 42 Model-R loss scale:

```text
524288 -> 262144
```

Overflow engineering policy:

```text
61ec4762487c
```

---

# 12. Final six-model provenance and hashes

A Google Drive FUSE persistence/quota incident caused four model directories to be missing after the original scientific runs.

Two seed-42 models were recovered exactly.  
Four seed-123/2026 models were deterministically reproduced and matched the original scientific SHA256 values byte-for-byte.

```text
seed 42 Model-R
78daac294df3438bba72a1eeb35024c543ffc9e7aa78a643f144c431bf823c99

seed 42 Model-V
5472a992eb75acc5eaede24254c601679151d3eb4b9a1423fc67c80a1c5c3a90

seed 123 Model-R
53da37dcbd5ca2ada3d707890c9d839e93b9133c2d684bbad3bccd8a2e5d4c84

seed 123 Model-V
7be38e2def25d35408024f3156f0c662614657d527d02241882b30c5e2472e88

seed 2026 Model-R
130d4bdc1e77312b4d65fb2719791121f07a00a4fb47602fe307aa2577864754

seed 2026 Model-V
92ed977edc8b977e291a8707d2a1aa85781ad68f0746c7c7522b18278855b86c
```

Final integrity:

```text
canonical models                   6/6
exact original SHA matches         6/6
original recovered                 2
exact deterministic reproductions  4
paired initialization              PASS all seeds
test evaluated during training     False
```

---

# 13. Validation diagnostics

Diagnostic only:

```text
seed 42 Model-R   loss .354153   F1 .645421   acc .885600
seed 42 Model-V   loss .260442   F1 .891585   acc .906267

seed 123 Model-R  loss .353616   F1 .649956   acc .885778
seed 123 Model-V  loss .256564   F1 .893302   acc .908089

seed 2026 Model-R loss .353542   F1 .640043   acc .884756
seed 2026 Model-V loss .257444   F1 .892859   acc .907911
```

Do not use R-vs-V validation/test F1 differences to claim supervision-source superiority because the targets differ.

---

# 14. Blind test inference

Test N:

```text
22,500
```

Canonical test row-order SHA256:

```text
ee4efe4d3f5e620c36f56923e4ab3481a65cdace75fae984b44cab009a508ded
```

Probability-artifact hashes:

```text
seed 42 Model-R
7c16acbf2547f09ec2c1d58406b541254e94375e63269126f75edb0fab7f7a05

seed 42 Model-V
537ee8517e58f9e07891440c7545fc7c983c87354311c9457855b922d53237a5

seed 123 Model-R
95853e41f906e1e2de17e308b59ebf4957f59b4a1eced265356f378a0614075f

seed 123 Model-V
6646d4f9c0fa1022b7f5fe7eef483a79a3e92bdb3e8018d51cdda83c05c40226

seed 2026 Model-R
7b5d0ddbc75c08301d4eb4f0a7eae6e4c27190d11515ebcc18676a41f8e22278

seed 2026 Model-V
4b550ae12fbddf380a41ac38a5b6e5e918c3ebc19c75e87e1a5dcd94ee38f7c3
```

No H4 testing was done during blind inference.

---

# 15. Jensen–Shannon divergence implementation

Primary outcome:

> per-review JSD between Model-R and Model-V predictive distributions, averaged across three paired seeds.

Natural logarithms are mandatory.

\[
M = (P_R + P_V)/2
\]

\[
JSD(P_R,P_V)
=
0.5 KL(P_R||M)
+
0.5 KL(P_V||M)
\]

Range:

\[
0 <= JSD <= ln(2)
\]

Reference implementation:

```python
import numpy as np

def jsd_natural_log(p, q, eps=1e-12):
    p = np.asarray(p, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)

    p = np.clip(p, eps, 1.0)
    q = np.clip(q, eps, 1.0)

    p = p / p.sum(axis=-1, keepdims=True)
    q = q / q.sum(axis=-1, keepdims=True)

    m = 0.5 * (p + q)

    kl_pm = np.sum(p * np.log(p / m), axis=-1)
    kl_qm = np.sum(q * np.log(q / m), axis=-1)

    return 0.5 * kl_pm + 0.5 * kl_qm
```

Do not substitute an ambiguous Jensen-Shannon **distance** implementation.

Normalized secondary JSD:

```python
jsd_normalized = jsd / np.log(2.0)
```

Hashes:

```text
3-seed JSD matrix
40cbe58d590b34bc1279b56b325156cc9f10a8a75fc6eb316ed8894facfee2c1

primary mean-seed JSD
2688ce3f06ad8eb5f16bfc52b5f3185372838f92ed983f9afc334154cb739903
```

---

# 16. Primary H4 implementation

Primary model:

```text
mean_seed_jsd ~ disagreement
```

Unit:

```text
review
```

Not `seed x review`.

Inference:

```text
OLS
cluster-robust SE by duplicate_group_id
small-sample correction = True
df correction = True
use_t = True
```

Authoritative implementation pattern:

```python
import numpy as np
import statsmodels.api as sm

def fit_primary_h4(data):
    data = data.reset_index(drop=True)

    y = data["mean_seed_jsd"].to_numpy(dtype=np.float64)
    d = data["disagreement"].to_numpy(dtype=np.float64)

    X = np.column_stack([
        np.ones(len(data), dtype=np.float64),
        d,
    ])

    groups = (
        data["duplicate_group_id"]
        .astype(str)
        .to_numpy()
    )

    fit = sm.OLS(y, X).fit(
        cov_type="cluster",
        cov_kwds={
            "groups": groups,
            "use_correction": True,
            "df_correction": True,
        },
        use_t=True,
    )

    ci = np.asarray(fit.conf_int(alpha=0.05))

    return {
        "beta": float(fit.params[1]),
        "se": float(fit.bse[1]),
        "t": float(fit.tvalues[1]),
        "p": float(fit.pvalues[1]),
        "ci_low": float(ci[1, 0]),
        "ci_high": float(ci[1, 1]),
    }
```

Decision rule:

```python
h4_supported = (
    beta > 0
    and ci_low > 0
)
```

No app adjustment.  
No rating adjustment.  
No alternative primary model.

Frozen result:

```text
N                      22,500
agreement              13,196
disagreement            9,304
clusters               15,921
singleton clusters     15,286
maximum cluster size    1,106

mean JSD agreement      0.05190023
mean JSD disagreement   0.40646891
beta                    0.35456868
cluster-robust SE       0.00610784
95% CI                  0.34259663–0.36654073
t                       58.05144
software p              numerical underflow to 0
report as                p < .001
H4                      SUPPORTED
```

Never report `p = 0`.

---

# 17. Large-cluster sensitivity — authoritative hotfix

The original Cell 64 is superseded because it caused pandas index misalignment after cluster exclusion:

```text
ValueError: The indices for endog and exog are not aligned
```

Authoritative code is Cell 64A, which resets the subset index and/or uses positional NumPy arrays.

Final scenarios:

```text
all clusters            beta 0.354569
exclude largest 1       beta 0.355058
exclude largest 5       beta 0.348804
exclude largest 10      beta 0.347277
```

Maximum absolute relative beta change:

```text
2.056%
```

All 95% CIs remained entirely positive.

This is post-primary sensitivity only and does not redefine H4.

---

# 18. Exploratory severity analysis

On the RQ4 test set:

```python
severity = np.abs(
    rating_target.astype(int)
    - vader_target.astype(int)
)
```

Target IDs:

```text
0 Negative
1 Neutral
2 Positive
```

Frozen means:

```text
S0 agreement              0.051900
S1 adjacent disagreement  0.440888
S2 extreme disagreement   0.319494
```

Contrasts:

```text
S1 - S0   0.388988
95% CI    0.375668–0.402309
Holm p    < .001

S2 - S0   0.267594
95% CI    0.249875–0.285312
Holm p    < .001

S2 - S1  -0.121395
95% CI   -0.143373 to -0.099417
Holm p    < .001
```

Observed order:

```text
S0 < S2 < S1
```

The categorical non-monotonic result is primary for this exploratory analysis. The linear trend is only a descriptor.

---

# 19. Transition-level explanation

Frozen disagreement transitions:

```text
Positive -> Neutral   N=2,743   mean JSD=0.518354
Negative -> Neutral   N=3,119   mean JSD=0.446303
Neutral  -> Positive  N=543     mean JSD=0.172044
Neutral  -> Negative  N=261     mean JSD=0.121376
Negative -> Positive  N=2,206   mean JSD=0.323178
Positive -> Negative  N=432     mean JSD=0.300678
```

No transition-specific hypothesis tests were performed.

Interpretation:

> The non-monotonic severity result is descriptively attributable to directional transition composition, not label distance alone.

---

# 20. Application-level RQ4 description

For all six applications:

```text
mean JSD(disagreement) > mean JSD(agreement)
```

Summary:

```text
6 / 6 applications positive
```

No app-specific hypothesis tests.  
No app x disagreement interaction test.  
Do not claim equal effect magnitude across applications.

---

# 21. Secondary prediction diagnostics

Three-seed review-level hard R-vs-V prediction disagreement:

```text
weak-label agreement       9.1518%
weak-label disagreement   79.9871%
```

Per seed:

```text
seed 42   agreement 0.088587   disagreement 0.795894
seed 123  agreement 0.094498   disagreement 0.802343
seed 2026 agreement 0.091467   disagreement 0.801376
```

Seed-count distribution:

```text
Agreement group
0/3 seeds  88.9133%
1/3         1.9476%
2/3         1.9097%
3/3         7.2295%

Disagreement group
0/3 seeds  16.7885%
1/3         2.7837%
2/3         4.1058%
3/3        76.3220%
```

Entropy/confidence:

```text
Mean paired entropy
agreement      0.198451
disagreement   0.351998

Mean paired max confidence
agreement      0.937767
disagreement   0.873573
```

---

# 22. Within-supervision test diagnostics

Model-R is evaluated only against `rating_target`.

Model-V is evaluated only against `vader_target`.

Three-seed summary:

```text
Model-R
accuracy mean  0.885437
accuracy SD    0.000703
macro-F1 mean  0.640817
macro-F1 SD    0.002286

Model-V
accuracy mean  0.905215
accuracy SD    0.000549
macro-F1 mean  0.890355
macro-F1 SD    0.000657
```

Do not rank the two supervision sources from these metrics.

---

# 23. Final RQ4 freeze

Freeze artifact:

```text
/content/drive/MyDrive/IGAR_Paper1/phase3/rq4_final/statistics/
RQ4_FINAL_SCIENTIFIC_FREEZE_5b7ffaa036af.json
```

Status:

```text
training                      CLOSED / PASS
test inference                CLOSED / PASS
paired JSD                    CLOSED / PASS
primary H4                    CLOSED / SUPPORTED
large-cluster sensitivity     CLOSED / PASS
severity exploratory          CLOSED / PASS
application description       CLOSED / PASS
transition exploratory        CLOSED / PASS
secondary diagnostics         CLOSED / PASS
additional RQ4 tests          NOT PLANNED
```

---

# 24. Paper-ready source-map audit

The automatic `rq_guess` inventory was heuristic and is **not authoritative**.

Manual source resolution is authoritative.

Locked source map:

```text
/content/drive/MyDrive/IGAR_Paper1/paper_ready/manifests/
Paper1_FINAL_Scientific_Source_Map_LOCKED.json
```

Manual resolutions:

```text
RQ2 transition
-> Table3_RQ2_Transition_Structure.csv

RQ2 app/domain structure
-> Table4_RQ2_Domain_Disagreement_Severity.csv

RQ3 paper-ready primary model
-> Table5_RQ3_Primary_Adjusted_OR.csv
```

---

# 25. Final paper tables

```text
Table 1
Table1_RQ1_WeakLabel_Agreement_Overall_PerApp.csv

Table 2A
Table2A_RQ1_WeakLabel_Transition_Counts.csv

Table 2B
Table2B_RQ1_WeakLabel_Transition_RowPercent.csv

Table 3
Table3_RQ3_Primary_Adjusted_OR.csv

Table 4
Table4_RQ4_Primary_JSD.csv
```

All main-paper table copies were verified byte-identical to locked sources.

---

# 26. Final paper figures

```text
Figure 1
Figure1_Study_Framework_FINAL.png
Figure1_Study_Framework_FINAL.pdf

Figure 2
Figure2_WeakLabel_Transition_Heatmap.png
Figure2_WeakLabel_Transition_Heatmap.pdf

Figure 3
Figure3_Disagreement_By_Rating_And_Application_FINAL.png
Figure3_Disagreement_By_Rating_And_Application_FINAL.pdf

Figure 4
Figure4_RQ3_Adjusted_OR_Forest_FINAL.png
Figure4_RQ3_Adjusted_OR_Forest_FINAL.pdf

Figure 5
Figure5_RQ4_JSD_Distribution.png
Figure5_RQ4_JSD_Distribution.pdf
```

Figure 1 authoritative conceptual provenance:

```text
IGAR dataset -> Frozen RQ4 cohort
```

Weak-label disagreement is:

```text
analysis grouping / predictor
```

not a cohort-generation mechanism.

---

# 27. Authoritative vs superseded code

## 27.1 Authoritative final sequence

```text
Gate 5B frozen cohort
Gate 6B strict deterministic protocol
Cell 60A final deterministic training/reproduction engine
Cells 60B–E exact deterministic missing-model reproductions
Cell 60F six-model integrity audit
Cell 59 recovery-aware final audit
Cell 61 blind test inference
Cell 62 paired JSD construction
Cell 63 primary H4
Cell 64A large-cluster sensitivity HOTFIX
Cell 65 severity exploratory
Cell 66 app-level descriptive heterogeneity
Cell 67 transition-level explanation
Cell 68 secondary prediction diagnostics
Cell 69 RQ4 scientific freeze
Cell 70A artifact inventory
Cell 70B source resolver
Cell 70C source-map lock and table package
Cell 70D figure-source lock
Cell 70E initial Figures 2–5
Cell 70F final QC refinement for Figures 3–4
Cell 71A corrected final Figure 1
Cell 72A Results architecture
```

## 27.2 Superseded — do not use

```text
Initial Cell 64
Reason: pandas endog/exog index misalignment.

Initial Figure 1 from Cell 71
Reason: could imply RQ4 cohort was generated from disagreement.

Initial Figure 3/4 files from Cell 70E
Reason: manuscript uses visual-QC-refined Cell 70F versions.
Scientific values were unchanged.
```

---

# 28. Minimal reproduction order

```text
01. Verify raw dataset SHA256.
02. Recreate/verify rating-derived weak labels.
03. Recreate/verify translation-mediated VADER weak labels.
04. Verify RQ1 counts and kappa.
05. Construct disagreement and severity.
06. Reproduce RQ2 transition/star/application structure.
07. Create deterministic row_id.
08. Normalize text and create duplicate_group_id.
09. Exclude only 19 extra exact full-row duplicates for primary RQ3.
10. Fit primary RQ3 logistic model with cluster-robust SE.
11. Run locked RQ3 sensitivity analyses.
12. Reproduce Gate 6A tokenizer/token-length audit.
13. Reuse frozen Gate 5B cohort when available.
14. Verify cohort SHA and assignment SHA.
15. Verify tokenized-cohort SHA.
16. Train paired Model-R/Model-V for seeds 42, 123, 2026.
17. Verify all six final model SHA256 values.
18. Perform blind test inference.
19. Verify test row-order SHA and six probability hashes.
20. Compute natural-log per-seed JSD.
21. Verify JSD hashes.
22. Merge frozen test metadata only after JSD construction.
23. Fit primary H4 exactly once.
24. Run post-primary sensitivity/secondary analyses.
25. Freeze RQ4.
26. Generate paper tables/figures only from frozen artifacts.
```

---

# 29. Recommended public repository structure

```text
IGAR-Paper1-Reproducibility/
|
|-- README.md
|-- LICENSE
|-- CITATION.cff
|
|-- environment/
|   |-- requirements-lock.txt
|   |-- pip-freeze.txt
|   `-- runtime-info.txt
|
|-- config/
|   |-- protocol.json
|   |-- model_config.json
|   `-- hashes.json
|
|-- src/
|   |-- 01_verify_raw_data.py
|   |-- 02_construct_weak_labels.py
|   |-- 03_rq1_rq2.py
|   |-- 04_duplicate_groups.py
|   |-- 05_rq3.py
|   |-- 06_gate6a_token_audit.py
|   |-- 07_build_or_verify_frozen_cohort.py
|   |-- 08_train_paired_indobert.py
|   |-- 09_blind_test_inference.py
|   |-- 10_construct_jsd.py
|   |-- 11_primary_h4.py
|   |-- 12_secondary_rq4.py
|   `-- 13_generate_paper_artifacts.py
|
|-- notebooks/
|   `-- original_final_colab.ipynb
|
|-- manifests/
|   |-- scientific_source_map.json
|   |-- figure_source_map.json
|   |-- rq4_final_freeze.json
|   `-- checksums.sha256
|
|-- outputs/
|   |-- tables/
|   |-- figures/
|   `-- logs/
|
`-- docs/
    `-- FINAL_CODE_AUDIT_AND_REPRODUCIBILITY.md
```

---

# 30. Environment release requirements

Already recorded:

```text
Python 3.13.15
torch 2.11.0+cu128
transformers 4.57.6
accelerate 1.14.0
tokenizers 0.22.2
safetensors 0.8.0
sentencepiece 0.2.2
```

Still recover exact versions for:

```text
numpy
pandas
scikit-learn
statsmodels
```

Recommended version-audit cell:

```python
import sys
import torch
import transformers
import accelerate
import tokenizers
import safetensors
import sentencepiece
import numpy
import pandas
import sklearn
import statsmodels

print("Python:", sys.version)
print("PyTorch:", torch.__version__)
print("Transformers:", transformers.__version__)
print("Accelerate:", accelerate.__version__)
print("Tokenizers:", tokenizers.__version__)
print("SafeTensors:", safetensors.__version__)
print("SentencePiece:", sentencepiece.__version__)
print("NumPy:", numpy.__version__)
print("Pandas:", pandas.__version__)
print("scikit-learn:", sklearn.__version__)
print("statsmodels:", statsmodels.__version__)
```

Also export:

```bash
pip freeze > pip-freeze.txt
```

---

# 31. Standard hash verification helper

```python
from pathlib import Path
import hashlib

def sha256_file(path):
    path = Path(path)
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()

def assert_sha256(path, expected):
    observed = sha256_file(path)

    assert observed == expected, (
        f"SHA256 mismatch\n"
        f"path     : {path}\n"
        f"expected : {expected}\n"
        f"observed : {observed}"
    )

    return observed
```

---

# 32. Key immutable hashes

```text
Raw dataset
852c8b662224bd62418ef7b7dac15b9e43c9a6b4cdf0fef6239042203c2eccb0

Frozen cohort assignment
bce0a04a9781ffe05a580c5af83d937a0df93e023bcdbac82de04d205b36a7e1

Frozen 150k cohort
ba13d30077a39e5aaacd6058c07454e31b0d938ebc949ce09edea7bc5a235912

Tokenized cohort
e99c92c57ae28350c268a51a9cef66f9f44ade95a36d2fc61947ed5ff8ce6272

Test row order
ee4efe4d3f5e620c36f56923e4ab3481a65cdace75fae984b44cab009a508ded

3-seed JSD matrix
40cbe58d590b34bc1279b56b325156cc9f10a8a75fc6eb316ed8894facfee2c1

Primary mean-seed JSD
2688ce3f06ad8eb5f16bfc52b5f3185372838f92ed983f9afc334154cb739903
```

Model and probability hashes are listed in Sections 12 and 14.

---

# 33. Scientific reporting locks

Allowed wording:

```text
weak-label disagreement
association
prediction sensitivity
prediction divergence
translation-mediated VADER weak label
rating-derived weak label
```

Avoid without independent ground truth:

```text
mislabeled review
incorrect label
true sentiment label
VADER error
rating error
ground-truth superiority
```

Acceptable RQ4 wording:

> Reviews exhibiting disagreement between the two weak-label sources showed substantially greater Transformer prediction divergence across supervision conditions.

Do not state causal failure from "noisy/mislabeled" reviews.

---

# 34. Reproducibility gaps before public release

## Gap 1 — exact training-engine source

The current audit record does not contain the complete source text of final Cell 60A.

Required action:

```text
Export Cell 60A and Cells 60B–E from the final Colab notebook
to src/08_train_paired_indobert.py, while preserving the exact notebook.
```

This is the most important remaining gap.

## Gap 2 — exact row_id / duplicate_group_id source

Required action:

```text
Export deterministic row_id generation function.
Export duplicate_group_id hash-generation function.
```

## Gap 3 — complete package versions

Record exact final versions of:

```text
numpy
pandas
scikit-learn
statsmodels
```

## Gap 4 — raw data acquisition provenance

Document:

```text
dataset DOI/version
download date
exact filename
raw SHA256
license/redistribution note
```

## Gap 5 — translation reproducibility

If IGAR already distributes the translated/VADER fields used in this paper, use those frozen fields.

If translation must be regenerated, record:

```text
translation provider/tool
tool version
source/target language
error/retry policy
date when provider is not version-stable
```

External translation services can change and may prevent byte-identical regeneration.

---

# 35. Successful independent replication criteria

Preferred exact replication should match:

```text
raw dataset SHA
cohort SHA
split-assignment SHA
six final model SHA values
six probability-artifact SHA values
test-row-order SHA
JSD matrix SHA
mean-seed JSD SHA
primary beta / SE / CI
H4 decision
```

If a materially different hardware/runtime prevents byte-identical weights, a secondary computational-reproducibility tier may require:

```text
same frozen cohort
same checkpoint revision
same training protocol
same seeds
same primary direction
effect estimate within a predeclared numerical tolerance
same H4 decision
```

Because byte-identical deterministic reproduction was achieved for four missing models in this study, exact SHA matching remains the preferred target under the locked environment.

---

# 36. Final audit checklist

```text
[PASS] Raw dataset checksum recorded
[PASS] RQ1 definitions frozen
[PASS] RQ2 definitions frozen
[PASS] RQ3 formula frozen
[PASS] Duplicate-cluster inference rule frozen
[PASS] RQ4 cohort frozen
[PASS] Model checkpoint + revision frozen
[PASS] Training hyperparameters frozen
[PASS] Deterministic paired-seed protocol frozen
[PASS] All six final model hashes recorded
[PASS] Test row-order hash recorded
[PASS] All six probability hashes recorded
[PASS] JSD definition frozen
[PASS] JSD hashes recorded
[PASS] Primary H4 model frozen
[PASS] Primary H4 decision rule frozen
[PASS] H4 result frozen
[PASS] Large-cluster sensitivity finalized with index-safe hotfix
[PASS] Severity analysis labeled exploratory
[PASS] App analysis labeled descriptive
[PASS] Transition analysis labeled exploratory
[PASS] Secondary diagnostics labeled secondary
[PASS] Cross-supervision F1 superiority claim prohibited
[PASS] RQ4 scientific freeze recorded
[PASS] Main-table source map locked
[PASS] Figure source map locked
[PASS] Figure 1 cohort provenance corrected
[PASS] Figures 1–5 final/locked

[OPEN] Export exact final Cell 60A–E training source
[OPEN] Export exact row_id / duplicate_group_id generation source
[OPEN] Record numpy/pandas/sklearn/statsmodels versions
[OPEN] Package raw-data acquisition and translation provenance
```

---

# 37. Final conclusion

The Paper 1 computational workflow is scientifically frozen and internally auditable. Its strongest reproducibility safeguards are:

1. frozen RQ4 cohort and cryptographic hashes;
2. paired Model-R/Model-V design where only the weak-supervision target changes;
3. strict deterministic training and exact model SHA verification;
4. blind test inference before H4 analysis;
5. explicit natural-log Jensen–Shannon divergence;
6. review-level primary inference with cluster-robust SE by `duplicate_group_id`;
7. a pre-locked H4 decision rule;
8. separation of confirmatory, sensitivity, exploratory, and descriptive analyses;
9. explicit prohibition against treating either weak-label source as ground truth;
10. authoritative source-map and table/figure locks for manuscript generation.

Before external release, export the exact final training-engine code, row/group ID generation functions, and complete environment lock. Once those packaging gaps are closed, the workflow can be distributed as a strong independent reproducibility package.
