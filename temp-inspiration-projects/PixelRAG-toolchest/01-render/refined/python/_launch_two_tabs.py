async def _launch_two_tabs(chrome_path: str, port: int, headless_shell: bool = False):
    """Launch one Chrome process, return 2 independent CDP connections (tabs)."""
    import websockets

    args = [chrome_path, f"--remote-debugging-port={port}"]
    if not headless_shell:
        args.append("--headless=new")
    args += [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--enable-gpu-rasterization",
        "--force-gpu-rasterization",
        "about:blank",
    ]

    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    ws_url_a = None
    for attempt in range(10):
        await asyncio.sleep(1)
        try:
            data = urllib.request.urlopen(
                f"http://localhost:{port}/json", timeout=3
            ).read()
            targets = json.loads(data)
            ws_url_a = pick_page_ws_url(targets)
            break
        except Exception:
            if attempt == 9:
                proc.kill()
                raise ConnectionError(f"Chrome port {port}")

    ws_a = await websockets.connect(
        ws_url_a, open_timeout=10, max_size=50 * 1024 * 1024
    )
    tab_a = WebsocketConnection(ws_a, proc)

    r = await tab_a.cdp("Target.createTarget", {"url": "about:blank"})
    target_id = r["result"]["targetId"]

    data2 = urllib.request.urlopen(f"http://localhost:{port}/json", timeout=3).read()
    targets2 = json.loads(data2)
    ws_url_b = None
    for t in targets2:
        if t.get("id") == target_id:
            ws_url_b = t["webSocketDebuggerUrl"]
            break
    if not ws_url_b:
        for t in targets2:
            if t["webSocketDebuggerUrl"] != ws_url_a:
                ws_url_b = t["webSocketDebuggerUrl"]
                break

    # Create a dummy proc wrapper for tab_b (so close() doesn't double-kill)
    class NoopProc:
        def send_signal(self, _):
            pass

        def wait(self, timeout=None):
            pass

        def kill(self):
            pass

    ws_b = await websockets.connect(
        ws_url_b, open_timeout=10, max_size=50 * 1024 * 1024
    )
    tab_b = WebsocketConnection(ws_b, NoopProc())

    return tab_a, tab_b, proc
