from pathlib import Path
import hashlib
EXPECTED = "ba13d30077a39e5aaacd6058c07454e31b0d938ebc949ce09edea7bc5a235912"

def sha256_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1024*1024), b""): h.update(c)
    return h.hexdigest()

def verify(path):
    got=sha256_file(path)
    if got!=EXPECTED: raise RuntimeError(f"Frozen cohort mismatch: {got}")
    return got
