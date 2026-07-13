def _golds_for(task: str, od: dict):
    if task in EXACT_MATCH_TASKS:
        g = (
            od.get("answers")
            or od.get("reference_list")
            or od.get("answer")
            or od.get("gt_answer")
        )
        return g if isinstance(g, list) else [g]
    return None
