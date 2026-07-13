def estimated_cost_usd(model: str, usage: dict) -> float | None:
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return None
    in_cost = usage["prompt_tokens"] / 1_000_000 * pricing["input_per_m"]
    out_cost = usage["completion_tokens"] / 1_000_000 * pricing["output_per_m"]
    return round(in_cost + out_cost, 6)
