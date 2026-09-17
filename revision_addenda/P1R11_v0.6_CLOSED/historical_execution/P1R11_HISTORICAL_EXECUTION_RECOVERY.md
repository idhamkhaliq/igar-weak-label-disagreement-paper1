# P1R-11 Historical Execution Recovery Record

**Status:** recovered execution evidence, not a substitute for the original raw script/output bundle.

This file records that P1R-11 stages A, B, D, E, F, C, the locked Decision Gate, and G were previously executed and documented in the Project history. All stages used preserved predictions/metadata; no retraining was performed.

## Recovered sequence

| Stage | Recovered status | Key evidence |
|---|---|---|
| 11A | PASS | 22,500 test reviews; 13,196 agreement; 9,304 disagreement; beta 0.35456868; preserved cohort and six prediction identities verified |
| 11B | GREEN | combined within-source D=1 JSD 0.00501638 vs cross-source 0.40646891; ratio 81.03x |
| 11D | GREEN | polarity-only N=15,385; beta 0.27880213; 95% CI [0.26104287, 0.29656139]; 78.63% retained |
| 11E | AMBER | Model-R Neutral F1 0.106882; shared-label V-R=-2.4503 pp; entropy ratio 1.4719x |
| 11F | Supportive | polarity-only cross/within=49.73x; polarity-restricted accuracy R=97.5968%, V=97.1183%; 2-class entropy ratio 1.3403x |
| 11C | GREEN | full-source singleton N=14,551; beta 0.29847002; 95% CI [0.29284181, 0.30409823]; 84.18% retained; singleton cross/within=59.60x |
| Decision Gate | AMBER FINAL | 4 GREEN + 1 AMBER + 0 RED |
| 11G | COMPLETE | S1 directional composition quantified; Neutral/Neutral cell directly measured; non-monotonicity downgraded to directional/class composition |

## Provenance boundary

- **Recovered historical execution record:** YES.
- **Original raw P1R-11 script bytes archived:** NOT YET VERIFIED.
- **Original machine-readable output bundle archived:** NOT YET VERIFIED.
- **Canonical 33 targets traceable to recovered stages:** YES (33/33).
- **New model training required:** NO.
- **Closure re-run from preserved inputs completed in the current addendum package:** NOT YET.

Therefore the package remains `OPEN`, but the correct description is now: **the P1R-11 analyses were executed and documented; the remaining work is archival reconstruction and closure verification, not scientific rediscovery.**
