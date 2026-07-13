async def _connect_cdp(port: int, retries: int = 5, delay: float = 1.0):
    """Connect to Chrome's CDP websocket endpoint."""
    import websockets

    for attempt in range(retries):
        try:
            data = urllib.request.urlopen(
                f"http://localhost:{port}/json", timeout=3
            ).read()
            targets = json.loads(data)
            # Pick a real page target — Chrome's built-in component extensions
            # (Cast/Media Router) expose background_page targets that show up
            # first in /json but never render navigations, hanging CDP capture.
            pages = [t for t in targets if t.get("type") == "page"] or targets
            ws = await websockets.connect(
                pages[0]["webSocketDebuggerUrl"],
                open_timeout=10,
                max_size=50 * 1024 * 1024,
            )
            return ws
        except Exception:
            if attempt < retries - 1:
                await asyncio.sleep(delay)
    raise ConnectionError(f"Failed to connect to Chrome on port {port}")
