import numpy as np
import statsmodels.api as sm

def fit_primary_h4(data):
    data = data.reset_index(drop=True)
    y = data["mean_seed_jsd"].to_numpy(dtype=np.float64)
    d = data["disagreement"].to_numpy(dtype=np.float64)
    X = np.column_stack([np.ones(len(data), dtype=np.float64), d])
    groups = data["duplicate_group_id"].astype(str).to_numpy()
    fit = sm.OLS(y, X).fit(
        cov_type="cluster",
        cov_kwds={"groups":groups,"use_correction":True,"df_correction":True},
        use_t=True,
    )
    ci=np.asarray(fit.conf_int(alpha=.05))
    result={"beta_disagreement":float(fit.params[1]),"cluster_robust_se":float(fit.bse[1]),"t_statistic":float(fit.tvalues[1]),"p_value":float(fit.pvalues[1]),"ci95_low":float(ci[1,0]),"ci95_high":float(ci[1,1])}
    result["h4_supported"] = result["beta_disagreement"] > 0 and result["ci95_low"] > 0
    return result
