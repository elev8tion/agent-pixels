def _fetch_status(api_url: str | None, timeout: float = 5.0) -> dict | None:
    """Fetch /status from a search-API URL for reproducibility tagging.

    Returns the JSON dict on success, or {"_error": str, "url": str} on failure
    (failure is recorded rather than raised so a missing service does not block the run).
    """
    if not api_url:
        return None
    import urllib.request

    base = api_url.rstrip("/")
    if base.endswith("/search"):
        base = base[: -len("/search")]
    status_url = base + "/status"
    try:
        with urllib.request.urlopen(status_url, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001 — best-effort capture
        return {"_error": f"{type(e).__name__}: {e}", "url": status_url}
