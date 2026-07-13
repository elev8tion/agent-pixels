async def generate_ground_truth(
    articles: list[dict],
    chrome_path: str,
    cache_dir: Path,
    seed: int,
    timeout_ms: int = 5000,
) -> dict[str, list[Path]]:
    cache_key = gt_cache_key(articles, seed)
    manifest_path = cache_dir / f"gt_{cache_key}.json"

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        all_exist = all(Path(p).exists() for paths in manifest.values() for p in paths)
        if all_exist:
            result = {k: [Path(p) for p in v] for k, v in manifest.items()}
            total = sum(len(v) for v in result.values())
            print(
                f"Ground truth cache hit: {len(result)} articles, {total} tiles",
                flush=True,
            )
            return result

    cache_dir.mkdir(parents=True, exist_ok=True)
    strategy = _make_gt_strategy(chrome_path, timeout_ms)
    await strategy.setup()
    try:
        results = await strategy.capture_articles(articles)
    finally:
        await strategy.teardown()

    ground_truth = {}
    for ac in results:
        tile_paths = []
        for tc in ac.tiles:
            tile_path = (
                cache_dir
                / f"gt_{cache_key}_{ac.article_path.replace('/', '_')}_{tc.tile_index:02d}.png"
            )
            if tc.image_bytes:
                tile_path.write_bytes(tc.image_bytes)
            tile_paths.append(tile_path)
        ground_truth[ac.article_path] = tile_paths

    manifest = {k: [str(p) for p in v] for k, v in ground_truth.items()}
    manifest_path.write_text(json.dumps(manifest))

    total = sum(len(v) for v in ground_truth.values())
    print(
        f"Ground truth generated: {len(ground_truth)} articles, {total} tiles",
        flush=True,
    )
    return ground_truth
