def score_batch(
    client_ctx: dict,
    args: argparse.Namespace,
    references: list[dict],
    batch: list[dict],
) -> list[dict]:
    prompt = build_prompt(references, batch)
    parsed = call_gemini_json(client_ctx, args.model, prompt, args.max_retries)
    if not isinstance(parsed, list):
        raise ValueError("Gemini response is not a JSON array")

    by_id = {}
    for item in parsed:
        if not isinstance(item, dict) or "id" not in item:
            continue
        by_id[int(item["id"])] = sanitize_decision(item, item["id"])

    decisions = []
    for row in batch:
        decision = by_id.get(row["row_id"])
        if decision is None:
            decision = {
                "id": row["row_id"],
                "naturalness": 0,
                "simpleqa_style_fit": 0,
                "keep": False,
                "reason": "missing_from_model_output",
            }
        decisions.append(decision)
    return decisions
