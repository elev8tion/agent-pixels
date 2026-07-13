async def run_and_verify(strategy, articles, ground_truth) -> dict:
    await strategy.setup()
    t0 = time.monotonic()
    try:
        article_captures = await strategy.capture_articles(articles)
    finally:
        wall_s = time.monotonic() - t0
        await strategy.teardown()

    # --- UNTIMED: decode + verify ---
    tiles_ok = 0
    tiles_bad = 0
    tiles_total = 0
    total_shot_ms = 0.0
    total_nav_ms = 0.0
    total_pixels = 0
    total_height_px = 0
    per_tile_shot_ms = []
    per_tile_nav_ms = []
    bad_examples = []
    is_lossy = strategy.fmt in ("jpeg",)

    for ac in article_captures:
        gt_tiles = ground_truth.get(ac.article_path, [])
        total_height_px += ac.page_height
        total_shot_ms += ac.total_shot_ms
        total_nav_ms += ac.total_nav_ms

        for tc in ac.tiles:
            tiles_total += 1
            total_pixels += VIEWPORT_WIDTH * tc.clip_h
            per_tile_shot_ms.append(tc.shot_ms)
            if tc.nav_ms > 0:
                per_tile_nav_ms.append(tc.nav_ms)

            if tc.tile_index >= len(gt_tiles):
                tiles_bad += 1
                bad_examples.append(f"{ac.article_path} tile {tc.tile_index}: no GT")
                continue

            img = decode_tile(tc)
            if img is None:
                tiles_bad += 1
                bad_examples.append(
                    f"{ac.article_path} tile {tc.tile_index}: decode failed"
                )
                continue

            ok, mean_diff = verify_tile(img, gt_tiles[tc.tile_index], is_lossy)
            if ok:
                tiles_ok += 1
            else:
                tiles_bad += 1
                if len(bad_examples) < 10:
                    bad_examples.append(
                        f"{ac.article_path} tile {tc.tile_index}: mean_diff={mean_diff:.2f}"
                    )

    for ac in article_captures:
        for tc in ac.tiles:
            if tc.raw_file_path:
                try:
                    os.unlink(tc.raw_file_path)
                except OSError:
                    pass

    correct_pct = tiles_ok / tiles_total * 100 if tiles_total > 0 else 0
    tps = tiles_total / wall_s if wall_s > 0 else 0
    ms_per_tile = total_shot_ms / tiles_total if tiles_total > 0 else 0
    articles_per_s = len(article_captures) / wall_s if wall_s > 0 else 0
    mpix_per_s = (total_pixels / 1_000_000) / wall_s if wall_s > 0 else 0
    shot_share = (
        total_shot_ms / (total_shot_ms + total_nav_ms)
        if (total_shot_ms + total_nav_ms) > 0
        else 0
    )

    # Latency percentiles
    sorted_shots = sorted(per_tile_shot_ms) if per_tile_shot_ms else [0]
    sorted_navs = sorted(per_tile_nav_ms) if per_tile_nav_ms else [0]

    def percentile(arr, p):
        idx = int(len(arr) * p / 100)
        return arr[min(idx, len(arr) - 1)]

    return {
        "name": strategy.name,
        "tiles_total": tiles_total,
        "tiles_ok": tiles_ok,
        "tiles_bad": tiles_bad,
        "correct_pct": correct_pct,
        "wall_s": wall_s,
        "tiles_per_s": tps,
        "ms_per_tile": ms_per_tile,
        "articles_per_s": articles_per_s,
        "mpix_per_s": mpix_per_s,
        "height_kpx_per_s": (total_height_px / 1000) / wall_s if wall_s > 0 else 0,
        "shot_pct": shot_share * 100,
        "bad_examples": bad_examples,
        # Latency distribution
        "shot_min": sorted_shots[0],
        "shot_p50": percentile(sorted_shots, 50),
        "shot_p95": percentile(sorted_shots, 95),
        "shot_p99": percentile(sorted_shots, 99),
        "shot_max": sorted_shots[-1],
        "nav_avg": sum(sorted_navs) / len(sorted_navs),
        "nav_p95": percentile(sorted_navs, 95),
    }
