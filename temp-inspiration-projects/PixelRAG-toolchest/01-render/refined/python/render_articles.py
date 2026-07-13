async def render_articles(
    articles: list[dict],
    output_dir: str,
    chrome_path: str = None,
    n_workers: int = 48,
    tile_height: int = TILE_HEIGHT,
    jpeg_quality: int = 85,
    n_compressors: int = 4,
) -> dict:
    """Render articles to JPEG tiles with async compression.

    Capture (Chrome → /dev/shm raw BGRA) and compression (raw → JPEG on disk)
    are fully decoupled.  Chrome workers never wait for compression.

    Args:
        articles: List of dicts with keys ``path`` (article ID) and
                  ``file`` (URL, http:// or absolute filesystem path).
        output_dir: Directory for output tile subdirectories.
        chrome_path: Path to Chrome binary.  Auto-detected if None.
        n_workers: Number of parallel Chrome processes (default 48).
        tile_height: Max tile height in pixels (default 8192).
        jpeg_quality: JPEG quality 1–100 (default 85).
        n_compressors: ProcessPoolExecutor workers for compression (default 4).

    Returns:
        dict with keys:
            ``total_tiles``     – number of tiles written
            ``wall_s``          – total wall-clock time in seconds
            ``tiles_per_s``     – throughput
            ``errors``          – count of capture/nav errors
            ``avg_capture_ms``  – average per-tile capture time (ms)
    """
    if not articles:
        return {
            "total_tiles": 0,
            "wall_s": 0.0,
            "tiles_per_s": 0.0,
            "errors": 0,
            "avg_capture_ms": 0.0,
        }

    if chrome_path is None:
        from ..chrome import find_chrome

        chrome_path = find_chrome()

    actual_workers = min(n_workers, len(articles))

    return await _run_render(
        articles=articles,
        output_dir=Path(output_dir),
        chrome_path=chrome_path,
        n_workers=actual_workers,
        tile_height=tile_height,
        jpeg_quality=jpeg_quality,
        n_compressors=n_compressors,
    )
