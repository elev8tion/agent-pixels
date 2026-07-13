def grade_exact_match(path: str) -> dict:
    rows = [json.loads(l) for l in open(path)]
    c = 0
    for d in rows:
        golds = _golds_for("nq", d.get("original_data", {}))
        if is_exact_match(strip_think(d.get("final_response")), golds):
            c += 1
    n = len(rows)
    return {
        "task": "exact_match",
        "file": path,
        "n": n,
        "correct": c,
        "incorrect": n - c,
        "unattempted": 0,
        "errors": 0,
        "score": c / n if n else 0.0,
    }
