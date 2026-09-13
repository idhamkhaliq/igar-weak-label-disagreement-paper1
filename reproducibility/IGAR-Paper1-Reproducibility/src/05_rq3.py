"""Locked primary RQ3 formula and cluster-robust logistic regression.

The primary manuscript table should still be verified against the frozen artifact
`Table5_RQ3_Primary_Adjusted_OR.csv` before release.
"""
import statsmodels.formula.api as smf

FORMULA = "disagreement ~ C(score, Treatment(reference=5)) + log_words + C(app, Treatment(reference='JMO'))"

def fit_primary(df):
    groups = df["duplicate_group_id"]
    fit = smf.logit(FORMULA, data=df).fit(
        disp=False,
        cov_type="cluster",
        cov_kwds={
            "groups": groups,
            "use_correction": True,
            "df_correction": True,
        },
    )
    return fit
