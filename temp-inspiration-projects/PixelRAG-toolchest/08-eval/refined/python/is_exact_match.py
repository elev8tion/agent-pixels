def is_exact_match(prediction: str, golds) -> bool:
    prediction = (prediction or "").replace("Exact Answer: ", "").strip()
    pred_norm = _normalize_text(prediction)
    return any(_normalize_text(str(g)) == pred_norm for g in golds)
