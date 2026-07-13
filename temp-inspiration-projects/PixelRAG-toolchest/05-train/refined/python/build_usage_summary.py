def build_usage_summary(client_ctx: dict, model: str) -> dict:
    usage = dict(client_ctx["usage"])
    pricing = MODEL_PRICING.get(model)
    estimated_cost_usd = None
    if pricing:
        estimated_cost_usd = (
            usage["prompt_tokens"] / 1_000_000 * pricing["input_per_m"]
            + usage["completion_tokens"] / 1_000_000 * pricing["output_per_m"]
        )
    return {
        **usage,
        "provider": client_ctx["provider"],
        "model": model,
        "estimated_cost_usd": estimated_cost_usd,
    }
