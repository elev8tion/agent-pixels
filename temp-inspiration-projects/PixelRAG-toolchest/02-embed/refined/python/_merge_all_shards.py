def _merge_all_shards(shard_files):
    """Single-pass: concat all shards, then numpy-vectorized global dedup.

    Returns dict of merged arrays + dim.
    """
    t0 = time.time()

    # First pass: quick count + dim check (mmap, no Python loop)
    total_raw = 0
    dim = None
    for sf in shard_files:
        with np.load(sf, mmap_mode="r") as data:
            n, d = data["embeddings"].shape
            if dim is None:
                dim = d
            assert d == dim, f"Dimension mismatch: {sf} has {d}, expected {dim}"
            total_raw += n
    print(f"Total raw vectors: {total_raw:,}, dim: {dim}")
    print(f"Allocating {total_raw * dim * 4 / 1e9:.1f} GB for float32 embeddings...")

    # Allocate output arrays
    all_emb = np.empty((total_raw, dim), dtype=np.float32)
    all_aids = np.empty(total_raw, dtype=np.int64)
    all_tiles = np.empty(total_raw, dtype=np.int32)
    all_chunks = np.empty(total_raw, dtype=np.int32)
    all_yoff = np.empty(total_raw, dtype=np.int32)
    all_theights = np.empty(total_raw, dtype=np.int32)

    # Concat all shards (no per-shard dedup — verified clean)
    row = 0
    for i, sf in enumerate(shard_files):
        with np.load(sf) as data:
            n = data["embeddings"].shape[0]
            all_emb[row : row + n] = data["embeddings"].astype(np.float32)
            all_aids[row : row + n] = data["article_ids"]
            all_tiles[row : row + n] = data["tile_indices"]
            all_chunks[row : row + n] = data["chunk_indices"]
            all_yoff[row : row + n] = data["y_offsets"]
            all_theights[row : row + n] = data["tile_heights"]
            row += n
        if (i + 1) % 100 == 0 or i == len(shard_files) - 1:
            print(
                f"  [{i + 1}/{len(shard_files)}] {row:,} vectors, {time.time() - t0:.0f}s"
            )

    print(f"Concat done: {row:,} vectors in {time.time() - t0:.0f}s")

    # Global dedup: numpy-vectorized unique on (article_id, tile, chunk)
    # Pack into single int64: article_id * 1e8 + tile * 1e4 + chunk
    print("Deduplicating...")
    t1 = time.time()
    keys = (
        all_aids[:row] * 100_000_000
        + all_tiles[:row].astype(np.int64) * 10_000
        + all_chunks[:row].astype(np.int64)
    )
    _, unique_idx = np.unique(keys, return_index=True)
    unique_idx.sort()  # preserve original order
    n_unique = len(unique_idx)
    n_dupes = row - n_unique
    print(
        f"Dedup done: {n_unique:,} unique, {n_dupes:,} duplicates removed in {time.time() - t1:.1f}s"
    )

    if n_dupes > 0:
        return {
            "embeddings": all_emb[unique_idx],
            "article_ids": all_aids[unique_idx],
            "tile_indices": all_tiles[unique_idx],
            "chunk_indices": all_chunks[unique_idx],
            "y_offsets": all_yoff[unique_idx],
            "tile_heights": all_theights[unique_idx],
            "dim": dim,
        }
    else:
        return {
            "embeddings": all_emb[:row],
            "article_ids": all_aids[:row],
            "tile_indices": all_tiles[:row],
            "chunk_indices": all_chunks[:row],
            "y_offsets": all_yoff[:row],
            "tile_heights": all_theights[:row],
            "dim": dim,
        }
