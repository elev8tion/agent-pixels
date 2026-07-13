def _sanitize_request_id(raw: str) -> str | None:
    """Return *raw* if it looks safe (≤64 chars, alphanumeric + ``-_``), else None."""
    if len(raw) > 64:
        return None
    if raw.replace("-", "").replace("_", "").isalnum():
        return raw.strip()
    return None
