def diff_shard_hashes(
    npz_path: str,
    shard_dir: str,
    hash_workers: int = 32,
) -> tuple[list[TileInfo], list[TileInfo], set[int]]:
    """Compare stored hashes in npz against current tile files on disk.

    Uses a thread pool to hash files in parallel (IO-bound on NVMe).

    Args:
        npz_path: Path to existing shard .npz file.
        shard_dir: Path to shard tile directory.
        hash_workers: Number of threads for parallel hashing.

    Returns:
        (stale_tiles, new_tiles, removed_rows):
            stale_tiles: TileInfos whose disk hash differs from stored hash.
            new_tiles: TileInfos on disk but not in npz at all.
            removed_rows: Row indices in npz whose tile_path no longer exists.
    """
    t0 = time.time()

    # Load stored index
    logger.info("Loading existing npz: %s", npz_path)
    data = np.load(npz_path)
    stored_paths = data["tile_paths"]  # S512
    stored_hashes = data["image_hashes"]  # S32
    logger.info(
        "Loaded %d stored embeddings in %.1fs", len(stored_paths), time.time() - t0
    )

    # Build index: tile_path -> (row_index, stored_hash)
    path_to_row: dict[str, tuple[int, str]] = {}
    for i in range(len(stored_paths)):
        p = (
            stored_paths[i].decode()
            if isinstance(stored_paths[i], bytes)
            else str(stored_paths[i])
        )
        h = (
            stored_hashes[i].decode()
            if isinstance(stored_hashes[i], bytes)
            else str(stored_hashes[i])
        )
        path_to_row[p] = (i, h)

    # Scan current tiles on disk
    disk_tiles = scan_shard_tiles(shard_dir)

    # Split into known (need hash check) vs new (not in npz)
    tiles_to_hash: list[TileInfo] = []
    new_tiles: list[TileInfo] = []
    seen_paths: set[str] = set()

    for ti in disk_tiles:
        seen_paths.add(ti.tile_path)
        if ti.tile_path in path_to_row:
            tiles_to_hash.append(ti)
        else:
            new_tiles.append(ti)

    # Parallel hash computation for known tiles
    stale_tiles: list[TileInfo] = []
    if tiles_to_hash:
        logger.info(
            "Hashing %d existing tiles (%d threads)...",
            len(tiles_to_hash),
            hash_workers,
        )
        t1 = time.time()
        matched = 0

        with ThreadPoolExecutor(max_workers=hash_workers) as pool:
            futures = {
                pool.submit(_hash_file, ti.tile_path): ti for ti in tiles_to_hash
            }
            pbar = tqdm(
                as_completed(futures),
                total=len(futures),
                desc="Hashing tiles",
                unit="tile",
            )
            for fut in pbar:
                ti = futures[fut]
                current_hash = fut.result()
                _row_idx, old_hash = path_to_row[ti.tile_path]
                if current_hash and current_hash != old_hash:
                    stale_tiles.append(ti)
                else:
                    matched += 1
                pbar.set_postfix(stale=len(stale_tiles), matched=matched)
            pbar.close()

        hash_rate = len(tiles_to_hash) / max(time.time() - t1, 0.001)
        logger.info(
            "Hashed %d tiles in %.1fs (%.0f tiles/s): %d matched, %d stale",
            len(tiles_to_hash),
            time.time() - t1,
            hash_rate,
            matched,
            len(stale_tiles),
        )

    # Rows whose source file was deleted
    removed_rows: set[int] = set()
    for p, (row_idx, _h) in path_to_row.items():
        if p not in seen_paths:
            removed_rows.add(row_idx)

    elapsed = time.time() - t0
    logger.info(
        "Diff complete in %.1fs: %d stale, %d new, %d removed, %d unchanged "
        "(stored=%d, on_disk=%d)",
        elapsed,
        len(stale_tiles),
        len(new_tiles),
        len(removed_rows),
        len(tiles_to_hash) - len(stale_tiles),
        len(stored_paths),
        len(disk_tiles),
    )
    return stale_tiles, new_tiles, removed_rows
