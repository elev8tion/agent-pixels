async def launch_websocket(
    chrome_path: str,
    port: int,
    headless_shell: bool = False,
    extra_args: list[str] | None = None,
) -> WebsocketConnection:
    """Launch Chrome via subprocess, connect via websocket."""
    import websockets

    args = [chrome_path, f"--remote-debugging-port={port}"]
    if not headless_shell:
        args.append("--headless=new")
    args += CHROME_ARGS
    if extra_args:
        args += extra_args
    args += ["about:blank"]

    # Reserve last 8 cores for compression workers
    n_cpus = os.cpu_count() or 128
    chrome_cores = list(range(max(1, n_cpus - 8)))

    def _preexec():
        try:
            os.sched_setaffinity(0, chrome_cores)
        except OSError:
            pass

    proc = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=_preexec,
    )

    for attempt in range(10):
        await asyncio.sleep(1)
        try:
            data = urllib.request.urlopen(
                f"http://localhost:{port}/json", timeout=3
            ).read()
            targets = json.loads(data)
            ws = await websockets.connect(
                pick_page_ws_url(targets),
                open_timeout=10,
                max_size=50 * 1024 * 1024,
            )
            return WebsocketConnection(ws, proc)
        except Exception:
            if attempt == 9:
                proc.kill()
                raise ConnectionError(f"Failed to connect to Chrome on port {port}")
