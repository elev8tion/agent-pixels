async def _cdp_send(ws, msg_id_ref: list, method: str, params: dict | None = None):
    """Send a CDP command and wait for its response."""
    msg_id_ref[0] += 1
    mid = msg_id_ref[0]
    msg = {"id": mid, "method": method}
    if params:
        msg["params"] = params
    await ws.send(json.dumps(msg))
    while True:
        r = json.loads(await asyncio.wait_for(ws.recv(), timeout=180))
        if r.get("id") == mid:
            if "error" in r:
                raise RuntimeError(f"CDP error: {r['error']}")
            return r.get("result", {})
