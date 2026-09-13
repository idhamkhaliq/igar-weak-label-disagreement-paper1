"""Token-length audit helper. Use checkpoint/revision from config/protocol.json."""
import numpy as np

def summarize_lengths(lengths):
    x = np.asarray(lengths)
    return {k: float(np.quantile(x,q)) for k,q in {"p50":.5,"p75":.75,"p90":.9,"p95":.95,"p99":.99,"p995":.995,"p999":.999}.items()} | {"N":int(x.size),"max":int(x.max()),"gt128":int((x>128).sum())}
