def _parse_judge_response(text: str) -> tuple[int, list[str]]:
    m = _JUDGE_LEN_PAT.search(text)
    n_pred = int(m.group(1)) if m else 0
    m = _JUDGE_OVERLAP_PAT.search(text)
    if not m:
        return n_pred, ["NULL"]
    tail = m.group(1).strip().split("\n\n", 1)[0].strip()
    if tail.upper().startswith("NULL"):
        return n_pred, ["NULL"]
    parts = [p.strip() for p in tail.split("###") if p.strip()]
    return n_pred, parts if parts else ["NULL"]
