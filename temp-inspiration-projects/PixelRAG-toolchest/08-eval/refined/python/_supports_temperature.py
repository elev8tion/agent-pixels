def _supports_temperature(model: str) -> bool:
    return "gpt-5" not in model
