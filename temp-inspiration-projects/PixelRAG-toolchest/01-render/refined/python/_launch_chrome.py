async def _launch_chrome(chrome_path: str, port: int) -> tuple:
    """Launch a headless Chrome and return (websocket, proc, user_data_dir)."""
    import websockets

    # Isolated profile per worker. Without --user-data-dir, a launch on a machine that
    # already has Chrome open forwards to the running instance (default profile) instead
    # of starting this headless renderer — navigation/screenshot then hang forever. A
    # unique dir also stops parallel workers from colliding on one profile. See issue #54.
    user_data_dir = tempfile.mkdtemp(prefix=f"pixelshot_chrome_{port}_")
    args = (
        # `--headless=new`: bare `--headless` is deprecated and hangs on modern Chrome.
        [
            chrome_path,
            f"--remote-debugging-port={port}",
            "--headless=new",
            f"--user-data-dir={user_data_dir}",
        ]
        + CHROME_ARGS
        + ["about:blank"]
    )
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for attempt in range(10):
        await asyncio.sleep(1)
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
            return ws, proc, user_data_dir
        except Exception:
            if attempt == 9:
                proc.kill()
                shutil.rmtree(user_data_dir, ignore_errors=True)
                raise ConnectionError(f"Failed to connect to Chrome on port {port}")
