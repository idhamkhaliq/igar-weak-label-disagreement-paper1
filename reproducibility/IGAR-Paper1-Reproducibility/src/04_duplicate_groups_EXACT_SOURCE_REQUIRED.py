"""
RELEASE BARRIER.

The scientific rule is frozen, but the exact row_id and duplicate_group_id hash-generation source
must be copied verbatim from the author's final notebook. tools/colab_close_gaps.py performs this
capture and creates src/04_exact_row_duplicate_id_cells.py. Do not silently replace it with an
invented hash/join convention.
"""
import re, unicodedata

def normalize_review_text(x):
    if x is None:
        return None
    x = unicodedata.normalize("NFC", str(x))
    return re.sub(r"\s+", " ", x.strip())
