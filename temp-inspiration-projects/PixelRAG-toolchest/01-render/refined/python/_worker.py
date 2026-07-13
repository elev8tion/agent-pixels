async def _worker(
    chrome_path: str,
    port: int,
    work_queue: asyncio.Queue,
    output_dir: Path,
    tile_height: int,
    quality: int,
    viewport_w: int,
    image_format: str,
    from_surface: bool,
    wait_network_idle: bool,
    worker_id: int,
    stats: dict,
    results: list,
):
    """Async worker: owns a Chrome process, pulls URLs from queue."""
    # Isolated profile per worker. Without --user-data-dir, a launch on a machine that
    # already has Chrome open forwards to the running instance (default profile) instead
    # of starting this headless renderer — navigation/screenshot then hang forever. A
    # unique dir also stops parallel workers from colliding on one profile. See issue #54.
    user_data_dir = tempfile.mkdtemp(prefix=f"pixelshot_chrome_{port}_")
    proc = subprocess.Popen(
        # `--headless=new`: the bare `--headless` is deprecated and hangs on modern
        # Chrome (e.g. google-chrome 149); `=new` works on both stock Chrome and the
        # patched headless_shell.
        [
            chrome_path,
            f"--remote-debugging-port={port}",
            "--headless=new",
            f"--user-data-dir={user_data_dir}",
        ]
        + BROWSER_ARGS
        + ["about:blank"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        await asyncio.sleep(3)
        ws = await _connect_cdp(port)
        msg_id_ref = [0]

        await _setup_page(ws, msg_id_ref, viewport_w, tile_height, wait_network_idle)
        await _drain_queue(
            ws,
            msg_id_ref,
            work_queue,
            output_dir,
            tile_height,
            quality,
            viewport_w,
            image_format,
            from_surface,
            wait_network_idle,
            worker_id,
            stats,
            results,
        )
        await ws.close()
    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(user_data_dir, ignore_errors=True)
