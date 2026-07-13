async def _page_ws_url_for_target(
    http_base: str, target_id: str, cdp_url: str, retries: int = 5, delay: float = 0.5
) -> str:
    """Resolve the page-level websocket URL for a freshly created ``targetId``.

    A freshly created target can momentarily be absent from ``/json``, so poll a
    few times (mirroring ``_connect_cdp``'s retry) before giving up. The blocking
    HTTP fetch runs in a thread so it doesn't block the event loop.
    """
    for attempt in range(retries):
        targets = await asyncio.to_thread(_fetch_json, f"{http_base}/json", cdp_url)
        for t in targets:
            if t.get("id") == target_id:
                return t["webSocketDebuggerUrl"]
        if attempt < retries - 1:
            await asyncio.sleep(delay)
    raise RuntimeError(f"Created target {target_id} not found in /json list")
