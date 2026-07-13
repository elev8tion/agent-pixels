async def _drain_queue(
    ws,
    msg_id_ref: list,
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
    """Pull URLs off the queue and capture each through ``ws`` until it's empty.

    Shared by the launch (``_worker``) and attach (``_attached_worker``) paths —
    they differ only in how ``ws`` is obtained, not in how work is processed.
    """
    while True:
        try:
            item = work_queue.get_nowait()
        except asyncio.QueueEmpty:
            break

        url = item["url"]
        stem = item["stem"]
        tile_dir = output_dir / f"{stem}.png.tiles"

        t0 = time.monotonic()
        try:
            n_tiles = await capture_url(
                ws,
                msg_id_ref,
                url,
                tile_dir,
                tile_h=tile_height,
                quality=quality,
                viewport_w=viewport_w,
                image_format=image_format,
                from_surface=from_surface,
                wait_network_idle=wait_network_idle,
            )
            stats["done"] += 1
            elapsed = time.monotonic() - t0
            logger.info("[w%d] %s → %d tiles (%.1fs)", worker_id, url, n_tiles, elapsed)
            results.append(tile_dir)
        except Exception as e:
            stats["failed"] += 1
            logger.warning("[w%d] FAIL %s: %s", worker_id, url, str(e)[:200])
