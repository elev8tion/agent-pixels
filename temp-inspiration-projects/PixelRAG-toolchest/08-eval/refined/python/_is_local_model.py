def _is_local_model(base_url: str) -> bool:
    return "localhost" in base_url or "127.0.0.1" in base_url
