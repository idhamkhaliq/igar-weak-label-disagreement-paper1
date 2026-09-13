"""Frozen weak-label definitions used by Paper 1."""

def rating_label(score):
    score = int(score)
    if score in (1,2): return "Negative"
    if score == 3: return "Neutral"
    if score in (4,5): return "Positive"
    raise ValueError(f"Unexpected score: {score}")

def vader_label(compound):
    compound = float(compound)
    if compound <= -0.05: return "Negative"
    if compound >= 0.05: return "Positive"
    return "Neutral"

CLASS_CODE = {"Negative": -1, "Neutral": 0, "Positive": 1}
MODEL_ID = {"Negative": 0, "Neutral": 1, "Positive": 2}

def disagreement(rating, vader):
    return int(rating != vader)

def severity(rating, vader):
    return abs(CLASS_CODE[rating] - CLASS_CODE[vader])
