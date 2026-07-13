def _lookup_and_copy_local_wiki_tiles(
    ex_id: str,
    url: str,
    tiles_dir: str,
    wiki_cache_dir: str,
    cut_height: int,
) -> list[str]:
    """Look up a Wikipedia URL in the local kiwix tile store, copy raw tiles, cut into strips.

    Args:
        ex_id: Example ID (used for output tile naming).
        url: Wikipedia URL.
        tiles_dir: Directory where cut tile strips are written ({ex_id}_tile_*.png).
        wiki_cache_dir: Directory where raw kiwix tile pages are cached ({ex_id}/).
        cut_height: Height of each output strip in pixels.

    Returns:
        Sorted list of cut tile paths.

    Raises:
        RuntimeError: If kiwix index unavailable, URL not found, or no tiles produced.
    """
    import glob as _glob
    import shutil
    import sys as _sys
    from PIL import Image

    # Return cached tiles if already cut
    existing = sorted(_glob.glob(os.path.join(tiles_dir, f"{ex_id}_tile_*.png")))
    if existing:
        return existing

    if not url or "wikipedia.org" not in url:
        raise RuntimeError(f"Not a Wikipedia URL: {url!r}")

    if not os.path.isdir(_KIWIX_OUTPUT_DIR) or not os.path.isfile(_KIWIX_ARTICLES_JSON):
        raise RuntimeError(f"kiwix tiles unavailable at {_KIWIX_OUTPUT_DIR}")

    if _WIKI_SCREENSHOT_DIR not in _sys.path:
        _sys.path.insert(0, _WIKI_SCREENSHOT_DIR)
    from scripts.build_index import batch_query_by_url as _batch_query

    redirects = _KIWIX_REDIRECTS_JSON if os.path.isfile(_KIWIX_REDIRECTS_JSON) else None
    results = _batch_query(
        _KIWIX_OUTPUT_DIR, [url], _KIWIX_ARTICLES_JSON, redirects_json=redirects
    )
    result = results.get(url)
    if result is None:
        raise RuntimeError(f"URL not found in local kiwix: {url}")

    # Copy raw kiwix tiles to wiki_cache_dir/{ex_id}/
    src_dir = os.path.join(_KIWIX_OUTPUT_DIR, result["tiles_dir"])
    article_cache = os.path.join(wiki_cache_dir, str(ex_id))
    if not os.path.exists(article_cache):
        if not os.path.isdir(src_dir):
            raise RuntimeError(f"kiwix tiles dir not on disk: {src_dir}")
        shutil.copytree(src_dir, article_cache)

    # Cut raw tiles into height=cut_height strips
    os.makedirs(tiles_dir, exist_ok=True)
    raw_tiles = sorted(
        f
        for f in os.listdir(article_cache)
        if f.endswith(".png") and f.startswith("tile_")
    )
    if not raw_tiles:
        raise RuntimeError(f"No tile PNGs found in {article_cache}")

    global_row = 0
    for raw_name in raw_tiles:
        raw_path = os.path.join(article_cache, raw_name)
        if os.path.getsize(raw_path) == 0:
            continue
        img = Image.open(raw_path)
        img.load()
        w, h = img.size
        y = 0
        while y < h:
            y2 = min(y + cut_height, h)
            strip = img.crop((0, y, w, y2))
            strip.save(os.path.join(tiles_dir, f"{ex_id}_tile_{global_row}_0.png"))
            strip.close()
            global_row += 1
            y += cut_height
        img.close()

    tile_paths = sorted(_glob.glob(os.path.join(tiles_dir, f"{ex_id}_tile_*.png")))
    if not tile_paths:
        raise RuntimeError(f"No strips cut for {ex_id} (source: {article_cache})")
    return tile_paths
