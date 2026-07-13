async def _connect_ws(ws_url: str):
    """Open a CDP websocket to an explicit ws URL (browser- or page-level)."""
    import websockets

    return await websockets.connect(ws_url, open_timeout=10, max_size=50 * 1024 * 1024)
