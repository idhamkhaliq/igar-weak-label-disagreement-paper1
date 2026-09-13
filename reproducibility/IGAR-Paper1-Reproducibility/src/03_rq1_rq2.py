"""Core RQ1/RQ2 constructions. Inferential table generation should use the frozen notebook/source export."""
import pandas as pd
from sklearn.metrics import cohen_kappa_score

LABELS = ["Negative","Neutral","Positive"]

def agreement_summary(df, rating_col="rating_label", vader_col="vader_label"):
    d = (df[rating_col] != df[vader_col])
    n = len(df); dn = int(d.sum()); an = n-dn
    return {
        "N": n,
        "agreement_n": an,
        "agreement_pct": 100*an/n,
        "disagreement_n": dn,
        "disagreement_pct": 100*dn/n,
        "cohen_kappa": float(cohen_kappa_score(df[rating_col], df[vader_col], labels=LABELS)),
    }

def transition_counts(df, rating_col="rating_label", vader_col="vader_label"):
    return pd.crosstab(df[rating_col], df[vader_col]).reindex(index=LABELS, columns=LABELS, fill_value=0)
