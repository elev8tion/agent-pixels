async def _run_batch(
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
    chrome_path: str,
) -> list[Path]:
    work_queue: asyncio.Queue = asyncio.Queue()
    stem_list = _derive_stems(urls, stems)
    for url, stem in zip(urls, stem_list):
        work_queue.put_nowait({"url": url, "stem": stem})

    stats = {"done": 0, "failed": 0}
    results: list[Path] = []
    base_port = 9400

    actual_workers = min(num_workers, len(urls))
    workers = [
        _worker(
            chrome_path,
            base_port + wid,
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

    logger.info("Batch complete: done=%d failed=%d", stats["done"], stats["failed"])
    return results
