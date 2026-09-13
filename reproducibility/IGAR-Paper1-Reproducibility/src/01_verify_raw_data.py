from pathlib import Path
import hashlib

EXPECTED = "852c8b662224bd62418ef7b7dac15b9e43c9a6b4cdf0fef6239042203c2eccb0"

def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def verify(path, expected=EXPECTED):
    observed = sha256_file(path)
    if observed != expected:
        raise RuntimeError(f"Dataset SHA mismatch: expected={expected} observed={observed}")
    return observed
