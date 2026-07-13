async def _launch_oneshot(
    chrome_path: str,
    port: int,
    headless_shell: bool,
    extra_args: list[str] | None,
):
    """Launch a fresh Chrome/headless_shell process and connect via websocket.

    Returns (WebsocketConnection, proc).  Polls every _POLL_INTERVAL seconds
    (much faster than the 1 s sleep in launch_websocket).
    """
    import websockets
    from .connection import WebsocketConnection

    args = [chrome_path, f"--remote-debugging-port={port}"]
    if not headless_shell:
        args.append("--headless=new")
    args += CHROME_ARGS
    if extra_args:
        args += extra_args
    args += ["about:blank"]

    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    last_exc: Exception | None = None
    for _ in range(_POLL_ATTEMPTS):
        await asyncio.sleep(_POLL_INTERVAL)
        try:
            data = urllib.request.urlopen(
                f"http://localhost:{port}/json", timeout=2
            ).read()
            targets = json.loads(data)
            ws = await websockets.connect(
                pick_page_ws_url(targets),
                open_timeout=5,
                max_size=50 * 1024 * 1024,
            )
            return WebsocketConnection(ws, proc), proc
        except Exception as e:
            last_exc = e

    proc.kill()
    raise ConnectionError(
        f"Failed to connect to Chrome on port {port} after "
        f"{_POLL_ATTEMPTS * _POLL_INTERVAL:.1f}s: {last_exc}"
    )
