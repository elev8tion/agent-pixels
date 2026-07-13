def _browser_ws_url(http_base: str, cdp_url: str) -> str:
    """Fetch the browser-level CDP websocket URL from ``/json/version``."""
    info = _fetch_json(f"{http_base}/json/version", cdp_url)
    try:
        return info["webSocketDebuggerUrl"]
    except (KeyError, TypeError) as e:
        raise RuntimeError(
            f"Could not reach CDP endpoint at {cdp_url}: "
            f"unexpected /json/version response (no webSocketDebuggerUrl)"
        ) from e
