import numpy as np
LN2 = np.log(2.0)

def jsd_natural_log(p, q, eps=1e-12):
    p = np.asarray(p, dtype=np.float64); q = np.asarray(q, dtype=np.float64)
    p = np.clip(p, eps, 1.0); q = np.clip(q, eps, 1.0)
    p = p / p.sum(axis=-1, keepdims=True); q = q / q.sum(axis=-1, keepdims=True)
    m = 0.5 * (p + q)
    return 0.5*np.sum(p*np.log(p/m),axis=-1) + 0.5*np.sum(q*np.log(q/m),axis=-1)

def normalized_jsd(p,q):
    return jsd_natural_log(p,q)/LN2
