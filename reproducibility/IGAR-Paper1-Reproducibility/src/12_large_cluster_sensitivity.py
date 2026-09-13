"""Authoritative index-safe post-primary sensitivity helper (Cell 64A logic)."""
import numpy as np
import statsmodels.api as sm

def fit_index_safe(data):
    data=data.reset_index(drop=True)
    y=data["mean_seed_jsd"].to_numpy(dtype=np.float64)
    d=data["disagreement"].to_numpy(dtype=np.float64)
    X=np.column_stack([np.ones(len(data),dtype=np.float64),d])
    groups=data["duplicate_group_id"].astype(str).to_numpy()
    fit=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":groups,"use_correction":True,"df_correction":True},use_t=True)
    ci=np.asarray(fit.conf_int(alpha=.05))
    return {"beta":float(fit.params[1]),"se":float(fit.bse[1]),"ci_low":float(ci[1,0]),"ci_high":float(ci[1,1])}
