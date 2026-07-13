async def _run_render(
    articles: list[dict],
    output_dir: Path,
    chrome_path: str,
    n_workers: int,
    tile_height: int,
    jpeg_quality: int,
    n_compressors: int,
) -> dict:
    raw_dir = Path("/dev/shm/pixelrag_render/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Semaphore: limit concurrent captures (CPU-bound) to n_workers // 2
    capture_limit = max(1, n_workers // 2)
    capture_sem = asyncio.Semaphore(capture_limit)

    # Compression: dedicated thread with its own multiprocessing.Pool.
    # Tiles are pushed to a thread-safe queue from capture workers.
    # The thread runs pool.starmap in batches, fully independent of asyncio.
    from multiprocessing import Pool as MPPool
    import queue as _queue
    import threading

    metrics = {
        "total_tiles": 0,
        "total_capture_ms": 0.0,
        "errors": 0,
    }

    compress_inbox: _queue.Queue = _queue.Queue()
    compress_done = threading.Event()

    n_cpus = os.cpu_count() or 128
    compress_cores = set(range(max(0, n_cpus - n_compressors), n_cpus))

    def _pool_init():
        try:
            os.sched_setaffinity(0, compress_cores)
        except OSError:
            pass

    def _compressor_thread():
        pool = MPPool(processes=n_compressors, initializer=_pool_init)
        # Warm up: ensure all workers are forked and idle before capture starts
        pool.map(int, range(n_compressors))
        async_results = []
        while True:
            item = compress_inbox.get()  # block until item available
            if item is None:
                break
            async_results.append(pool.apply_async(compress_tile, item))
        # Wait for all remaining
        for ar in async_results:
            try:
                ar.get(timeout=60)
            except Exception:
                pass
        pool.close()
        pool.join()
        compress_done.set()

    compress_thread = threading.Thread(target=_compressor_thread, daemon=True)
    compress_thread.start()

    base_port = _next_base_port()

    # Work-stealing queue
    work_q: asyncio.Queue = asyncio.Queue()
    for art in articles:
        work_q.put_nowait(art)

    # Launch Chrome workers
    connections: list[_Conn] = []
    frame_ids: list[str] = []

    logger.info(
        "Launching %d Chrome workers on ports %d-%d",
        n_workers,
        base_port,
        base_port + n_workers - 1,
    )
    for i in range(n_workers):
        ws, proc, user_data_dir = await _launch_chrome(chrome_path, base_port + i)
        conn = _Conn(ws, proc, user_data_dir)
        connections.append(conn)

    for i, conn in enumerate(connections):
        await conn.cdp("Page.enable")
        await conn.cdp(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": VIEWPORT_WIDTH,
                "height": tile_height,
                "deviceScaleFactor": 1,
                "mobile": False,
            },
        )
        ft = await conn.cdp("Page.getFrameTree")
        frame_ids.append(ft["result"]["frameTree"]["frame"]["id"])

    logger.info("All workers ready. Processing %d articles.", len(articles))
    t_start = time.monotonic()

    async def worker_task(wi: int):
        conn = connections[wi]
        main_fid = frame_ids[wi]

        while True:
            try:
                article = work_q.get_nowait()
            except asyncio.QueueEmpty:
                break

            art_path = article["path"]
            raw_file_val = article.get("file", "")
            target_url = (
                raw_file_val
                if raw_file_val.startswith("http")
                else f"file://{raw_file_val}"
            )

            # Make output tile dir: use path slug
            slug = art_path.replace("/", "_").replace(" ", "_")[:200] or "article"
            tile_dir = output_dir / f"{slug}.tiles"
            tile_dir.mkdir(parents=True, exist_ok=True)

            try:
                # --- NAV (outside semaphore — I/O bound) ---
                nav_event_fut = asyncio.ensure_future(
                    conn.wait_for_event(
                        "Page.frameStoppedLoading",
                        timeout=30.0,
                        filter_fn=lambda p: p.get("frameId") == main_fid,
                    )
                )
                try:
                    await conn.cdp("Page.navigate", {"url": target_url})
                except Exception as e:
                    nav_event_fut.cancel()
                    logger.warning("[w%d] nav failed for %s: %s", wi, art_path, e)
                    metrics["errors"] += 1
                    continue

                try:
                    await nav_event_fut
                except asyncio.TimeoutError:
                    logger.warning(
                        "[w%d] frameStoppedLoading timeout for %s", wi, art_path
                    )
                    metrics["errors"] += 1
                    continue

                # Wait for fonts + images, get page height
                try:
                    r = await conn.cdp(
                        "Runtime.evaluate",
                        {
                            "expression": _WAIT_FONTS_IMGS,
                            "awaitPromise": True,
                            "returnByValue": True,
                        },
                    )
                    page_h = r["result"]["result"]["value"]
                    if not page_h or page_h <= 0:
                        page_h = tile_height
                except Exception:
                    page_h = tile_height

                n_tiles = max(1, (page_h + tile_height - 1) // tile_height)
                n_written = 0
                tile_names = []

                for t in range(n_tiles):
                    clip_h = min(tile_height, page_h - t * tile_height)
                    if clip_h <= 28:
                        break

                    # Scroll + wait in-viewport images (outside semaphore)
                    if t > 0:
                        y = t * tile_height
                        try:
                            await conn.cdp(
                                "Runtime.evaluate",
                                {
                                    "expression": f"""new Promise(resolve => {{
                                    window.scrollTo(0, {y});
                                    requestAnimationFrame(() => requestAnimationFrame(() => {{
                                        const imgs = Array.from(document.images).filter(i => {{
                                            if (i.complete) return false;
                                            const r = i.getBoundingClientRect();
                                            return r.bottom > 0 && r.top < window.innerHeight;
                                        }});
                                        if (imgs.length === 0) return resolve();
                                        const timeout = new Promise(r => setTimeout(r, 500));
                                        const loaded = Promise.all(imgs.map(i => new Promise(r => {{
                                            i.addEventListener('load', r, {{once: true}});
                                            i.addEventListener('error', r, {{once: true}});
                                        }})));
                                        Promise.race([loaded, timeout]).then(resolve);
                                    }}));
                                }})""",
                                    "awaitPromise": True,
                                },
                            )
                        except Exception:
                            pass

                    # Acquire semaphore → capture → release (fine-grained)
                    raw_path = str(raw_dir / f"w{wi}_{slug}_{t}.raw")
                    out_path = str(tile_dir / f"tile_{t:04d}.jpg")

                    await capture_sem.acquire()
                    try:
                        t0 = time.monotonic()
                        r = await conn.cdp(
                            "Page.captureScreenshot",
                            {
                                "fromSurface": True,
                                "optimizeForSpeed": True,
                                "rawFilePath": raw_path,
                                "clip": {
                                    "x": 0,
                                    "y": t * tile_height,
                                    "width": VIEWPORT_WIDTH,
                                    "height": clip_h,
                                    "scale": 1,
                                },
                            },
                        )
                        shot_ms = (time.monotonic() - t0) * 1000
                    except Exception as e:
                        logger.warning(
                            "[w%d] capture failed tile %d of %s: %s", wi, t, art_path, e
                        )
                        metrics["errors"] += 1
                        continue
                    finally:
                        capture_sem.release()

                    if "error" in r.get("result", {}):
                        logger.warning(
                            "[w%d] CDP error tile %d of %s: %s",
                            wi,
                            t,
                            art_path,
                            r["result"]["error"],
                        )
                        metrics["errors"] += 1
                        continue

                    metrics["total_capture_ms"] += shot_ms

                    # Enqueue compression (non-blocking — capture continues)
                    compress_inbox.put((raw_path, out_path, jpeg_quality))
                    n_written += 1
                    tile_names.append(f"tile_{t:04d}.jpg")

                # Write manifest
                manifest = {
                    "path": art_path,
                    "url": target_url,
                    "page_height": page_h,
                    "tiles": tile_names,
                    "complete": True,
                }
                with open(tile_dir / "tiles.json", "w") as f:
                    json.dump(manifest, f)

                metrics["total_tiles"] += n_written
                logger.info(
                    "[w%d] %s → %d tiles (%.0f ms capture)",
                    wi,
                    art_path,
                    n_written,
                    shot_ms if n_tiles == 1 else 0,
                )

            except Exception as e:
                logger.warning("[w%d] unexpected error for %s: %s", wi, art_path, e)
                metrics["errors"] += 1

    # Run all workers concurrently
    await asyncio.gather(*[worker_task(i) for i in range(n_workers)])

    capture_wall_s = time.monotonic() - t_start
    total = metrics["total_tiles"]
    capture_tps = total / capture_wall_s if capture_wall_s > 0 else 0.0
    logger.info(
        "Capture done: %d tiles in %.1fs (%.1f tiles/s)",
        total,
        capture_wall_s,
        capture_tps,
    )

    # Wait for compression — run in thread to avoid blocking asyncio event loop
    import threading

    # Signal compression thread to finish, teardown Chrome in parallel
    compress_inbox.put(None)

    for conn in connections:
        try:
            await conn.close()
        except Exception:
            pass

    # Wait for compression to finish (runs in its own thread, no asyncio)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, compress_done.wait, 120)

    wall_s = time.monotonic() - t_start
    tps = total / wall_s if wall_s > 0 else 0.0

    logger.info(
        "Done: %d tiles in %.1fs (%.1f tiles/s, capture=%.1f tiles/s)",
        total,
        wall_s,
        tps,
        capture_tps,
    )
    return {
        "total_tiles": total,
        "wall_s": wall_s,
        "capture_wall_s": capture_wall_s,
        "capture_tiles_per_s": capture_tps,
        "tiles_per_s": tps,
        "errors": metrics["errors"],
        "avg_capture_ms": (metrics["total_capture_ms"] / total if total > 0 else 0.0),
    }
