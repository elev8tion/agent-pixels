def patch_shard(
    npz_path: str,
    shard_dir: str,
    gpu_ids: list[int],
    model: str = "Qwen/Qwen3-VL-Embedding-2B",
    batch_size: int = 512,
    io_workers: int = 8,
    compress_npz: bool = False,
    yes: bool = False,
    dry_run: bool = False,
    backend: str = "vllm",
    max_pixels: int | None = None,
    adapter_path: str | None = None,
) -> dict:
    """Patch an existing shard npz by re-embedding only changed/new tiles.

    1. Diff stored hashes vs disk files
    2. Show summary and ask for confirmation
    3. Re-embed stale + new tiles
    4. Update npz: replace stale rows, append new rows, drop removed rows

    Args:
        npz_path: Path to existing shard .npz.
        shard_dir: Path to shard tile directory.
        gpu_ids: GPU IDs to use.
        model: Model name or path.
        batch_size: Tiles per embed() call.
        yes: Skip confirmation prompt.
        dry_run: Only diff, don't embed or write.

    Returns:
        Dict with keys: npz_path, patched, added, removed, unchanged.
    """
    stale_tiles, new_tiles, removed_rows = diff_shard_hashes(npz_path, shard_dir)

    tiles_to_embed = stale_tiles + new_tiles
    if not tiles_to_embed and not removed_rows:
        logger.info("Nothing to patch — all hashes match")
        return {
            "npz_path": npz_path,
            "patched": 0,
            "added": 0,
            "removed": 0,
            "unchanged": True,
        }

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  Patch summary for {os.path.basename(npz_path)}")
    print(f"{'=' * 60}")
    print(f"  Stale (hash changed):  {len(stale_tiles):>8}  → re-embed")
    print(f"  New (not in npz):      {len(new_tiles):>8}  → embed")
    print(f"  Removed (file gone):   {len(removed_rows):>8}  → drop")
    print(f"  Total to embed:        {len(tiles_to_embed):>8}")
    print(f"{'=' * 60}\n")

    if dry_run:
        logger.info("Dry run — stopping before embedding")
        return {
            "npz_path": npz_path,
            "patched": len(stale_tiles),
            "added": len(new_tiles),
            "removed": len(removed_rows),
            "dry_run": True,
        }

    if not yes:
        answer = input("Proceed with patch? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            logger.info("Aborted by user")
            return {"npz_path": npz_path, "aborted": True}

    # Load existing data
    data = np.load(npz_path)
    old_embeddings = data["embeddings"]
    old_article_ids = data["article_ids"]
    old_tile_indices = data["tile_indices"]
    old_page_heights = data["page_heights"]
    old_viewport_widths = data["viewport_widths"]
    old_tile_heights = data["tile_heights"]
    old_image_hashes = data["image_hashes"]
    old_tile_paths = data["tile_paths"]
    shard_id = int(data["shard_id"])

    # Build stale path -> row index for replacement
    path_to_row: dict[str, int] = {}
    for i in range(len(old_tile_paths)):
        p = (
            old_tile_paths[i].decode()
            if isinstance(old_tile_paths[i], bytes)
            else str(old_tile_paths[i])
        )
        path_to_row[p] = i
    stale_row_indices = {path_to_row[ti.tile_path] for ti in stale_tiles}

    # Embed the changed + new tiles
    t_embed = time.time()
    if tiles_to_embed:
        logger.info(
            "Embedding %d tiles (%d stale + %d new) on GPUs %s",
            len(tiles_to_embed),
            len(stale_tiles),
            len(new_tiles),
            gpu_ids,
        )
        output_dir = os.path.dirname(npz_path)

        num_gpus = len(gpu_ids)
        if num_gpus == 1:
            partial_path = gpu_worker(
                gpu_ids[0],
                tiles_to_embed,
                model,
                batch_size,
                output_dir,
                backend,
                io_workers=io_workers,
                compress_npz=compress_npz,
                max_pixels=max_pixels,
                adapter_path=adapter_path,
            )
            partial_paths = [partial_path] if partial_path else []
        else:
            article_ids_list = sorted(set(t.article_id for t in tiles_to_embed))
            gpu_assignment = {
                aid: gpu_ids[i % num_gpus] for i, aid in enumerate(article_ids_list)
            }
            per_gpu: dict[int, list[TileInfo]] = {gid: [] for gid in gpu_ids}
            for ti in tiles_to_embed:
                per_gpu[gpu_assignment[ti.article_id]].append(ti)

            partial_paths = run_gpu_workers_parallel(
                per_gpu=per_gpu,
                gpu_ids=gpu_ids,
                model_path=model,
                batch_size=batch_size,
                result_dir=output_dir,
                backend=backend,
                io_workers=io_workers,
                compress_npz=compress_npz,
                max_pixels=max_pixels,
                adapter_path=adapter_path,
            )

        # Collect new embeddings
        new_emb, new_aids, new_tidx = [], [], []
        new_ph, new_vw, new_th = [], [], []
        new_ih, new_tp = [], []
        for pp in partial_paths:
            d = np.load(pp)
            new_emb.append(d["embeddings"])
            new_aids.append(d["article_ids"])
            new_tidx.append(d["tile_indices"])
            new_ph.append(d["page_heights"])
            new_vw.append(d["viewport_widths"])
            new_th.append(d["tile_heights"])
            new_ih.append(d["image_hashes"])
            new_tp.append(d["tile_paths"])
            try:
                os.remove(pp)
            except OSError:
                pass

        if new_emb:
            fresh_embeddings = np.concatenate(new_emb, axis=0)
            fresh_article_ids = np.concatenate(new_aids)
            fresh_tile_indices = np.concatenate(new_tidx)
            fresh_page_heights = np.concatenate(new_ph)
            fresh_viewport_widths = np.concatenate(new_vw)
            fresh_tile_heights = np.concatenate(new_th)
            fresh_image_hashes = np.concatenate(new_ih)
            fresh_tile_paths = np.concatenate(new_tp)
        else:
            tiles_to_embed = []  # embedding failed

    # Build path index for fresh results
    fresh_by_path: dict[str, int] = {}
    if tiles_to_embed:
        for i in range(len(fresh_tile_paths)):
            p = (
                fresh_tile_paths[i].decode()
                if isinstance(fresh_tile_paths[i], bytes)
                else str(fresh_tile_paths[i])
            )
            fresh_by_path[p] = i

    # Assemble final arrays: keep unchanged rows, replace stale, drop removed
    rows_to_drop = stale_row_indices | removed_rows
    keep_mask = np.ones(len(old_embeddings), dtype=bool)
    for r in rows_to_drop:
        keep_mask[r] = False

    parts_emb = [old_embeddings[keep_mask]]
    parts_aids = [old_article_ids[keep_mask]]
    parts_tidx = [old_tile_indices[keep_mask]]
    parts_ph = [old_page_heights[keep_mask]]
    parts_vw = [old_viewport_widths[keep_mask]]
    parts_th = [old_tile_heights[keep_mask]]
    parts_ih = [old_image_hashes[keep_mask]]
    parts_tp = [old_tile_paths[keep_mask]]

    if tiles_to_embed:
        parts_emb.append(fresh_embeddings)
        parts_aids.append(fresh_article_ids)
        parts_tidx.append(fresh_tile_indices)
        parts_ph.append(fresh_page_heights)
        parts_vw.append(fresh_viewport_widths)
        parts_th.append(fresh_tile_heights)
        parts_ih.append(fresh_image_hashes)
        parts_tp.append(fresh_tile_paths)

    final_emb = np.concatenate(parts_emb, axis=0)
    final_aids = np.concatenate(parts_aids)
    final_tidx = np.concatenate(parts_tidx)
    final_ph = np.concatenate(parts_ph)
    final_vw = np.concatenate(parts_vw)
    final_th = np.concatenate(parts_th)
    final_ih = np.concatenate(parts_ih)
    final_tp = np.concatenate(parts_tp)

    # Re-sort
    sort_idx = np.lexsort((final_tidx, final_aids))
    final_emb = final_emb[sort_idx]
    final_aids = final_aids[sort_idx]
    final_tidx = final_tidx[sort_idx]
    final_ph = final_ph[sort_idx]
    final_vw = final_vw[sort_idx]
    final_th = final_th[sort_idx]
    final_ih = final_ih[sort_idx]
    final_tp = final_tp[sort_idx]

    save_npz(
        npz_path,
        compressed=compress_npz,
        embeddings=final_emb,
        article_ids=final_aids,
        tile_indices=final_tidx,
        page_heights=final_ph,
        viewport_widths=final_vw,
        tile_heights=final_th,
        image_hashes=final_ih,
        tile_paths=final_tp,
        shard_id=np.int32(shard_id),
    )

    elapsed_total = time.time() - t_embed
    logger.info(
        "Patched %s in %.1fs: %d replaced, %d added, %d removed, %d total",
        npz_path,
        elapsed_total,
        len(stale_tiles),
        len(new_tiles),
        len(removed_rows),
        len(final_emb),
    )
    return {
        "npz_path": npz_path,
        "patched": len(stale_tiles),
        "added": len(new_tiles),
        "removed": len(removed_rows),
        "total": len(final_emb),
        "unchanged": False,
    }
