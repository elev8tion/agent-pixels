async def _run_batch_attached(
    urls: list[str],
    output_dir: Path,
    num_workers: int,
    tile_height: int,
    quality: int,
    viewport_w: int,
    image_format: str,
    from_surface: bool,
    wait_network_idle: bool,
    stems: list[str] | None,
    cdp_url: str,
) -> list[Path]:
    http_base = _http_base_from_cdp_url(cdp_url)
    browser_ws_url = _browser_ws_url(http_base, cdp_url)

    work_queue: asyncio.Queue = asyncio.Queue()
    stem_list = _derive_stems(urls, stems)
    for url, stem in zip(urls, stem_list):
        work_queue.put_nowait({"url": url, "stem": stem})

    stats = {"done": 0, "failed": 0}
    results: list[Path] = []

    # One fresh tab per worker against the single shared browser — no extra
    # processes, no interference with the user's existing tabs.
    actual_workers = min(num_workers, len(urls))
    workers = [
        _attached_worker(
            http_base,
            browser_ws_url,
            cdp_url,
            work_queue,
            output_dir,
            tile_height,
            quality,
            viewport_w,
            image_format,
            from_surface,
            wait_network_idle,
            wid,
            stats,
            results,
        )
        for wid in range(actual_workers)
    ]
    await asyncio.gather(*workers, return_exceptions=True)

    logger.info(
        "Batch complete (attached): done=%d failed=%d", stats["done"], stats["failed"]
    )
    return results
