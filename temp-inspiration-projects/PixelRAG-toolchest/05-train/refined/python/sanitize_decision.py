def sanitize_decision(raw: dict, row_id: int) -> dict:
    naturalness = raw.get("naturalness", 0)
    style_fit = raw.get("simpleqa_style_fit", 0)
    keep = raw.get("keep", False)
    reason = raw.get("reason", "")

    try:
        naturalness = int(naturalness)
    except Exception:
        naturalness = 0
    try:
        style_fit = int(style_fit)
    except Exception:
        style_fit = 0
    if isinstance(keep, str):
        keep = keep.strip().lower() in {"true", "yes", "1", "keep"}

    return {
        "id": int(row_id),
        "naturalness": max(0, min(5, naturalness)),
        "simpleqa_style_fit": max(0, min(5, style_fit)),
        "keep": bool(keep),
        "reason": str(reason).strip()[:200],
    }
