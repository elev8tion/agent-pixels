def embed_shard(
    shard_dir: str,
    output_dir: str,
    gpu_ids: list[int],
    model: str = "Qwen/Qwen3-VL-Embedding-2B",
    batch_size: int = 512,
    io_workers: int = 8,
    compress_npz: bool = False,
    reuse_workers: bool = False,
    skip_article_ids: set[int] | None = None,
    backend: str = "vllm",
    max_pixels: int | None = None,
    mode: str = "chunks",
    chunk_height: int | None = None,
    enforce_eager: bool = False,
    adapter_path: str | None = None,
) -> dict:
    """Scan a shard, embed across GPUs, merge results into a single .npz.

    Args:
        shard_dir: Path to shard directory.
        output_dir: Directory for output .npz file.
        gpu_ids: List of GPU IDs to use.
        model: Model name or path.
        batch_size: Tiles per embed call.
        skip_article_ids: Article IDs already embedded (for resume).
        backend: "vllm" or "sglang".

    Returns:
        Dict with keys: shard_dir, output_path, num_tiles, num_articles, elapsed_s.
    """
    t0 = time.time()
    os.makedirs(output_dir, exist_ok=True)

    # Extract shard_id from directory name
    shard_name = os.path.basename(shard_dir.rstrip("/"))  # e.g. "shard_042"
    try:
        shard_id = int(shard_name.split("_")[1])
    except (ValueError, IndexError):
        shard_id = 0

    # Scan images (chunks or tiles depending on mode)
    if mode == "chunks":
        tile_infos = scan_shard_chunks(shard_dir, skip_article_ids)
        unit = "chunks"
    else:
        tile_infos = scan_shard_tiles(shard_dir, skip_article_ids)
        unit = "tiles"
    if not tile_infos:
        logger.warning("No %s found in %s", unit, shard_dir)
        return {
            "shard_dir": shard_dir,
            "output_path": "",
            "num_tiles": 0,
            "num_articles": 0,
            "elapsed_s": time.time() - t0,
        }

    # Incremental: load existing .npz, detect new + updated chunks via mtime
    output_path = os.path.join(output_dir, f"shard_{shard_id:03d}.npz")
    existing_npz = None
    stale_keys: set[tuple[int, int, int]] = set()  # keys to replace in existing npz
    if os.path.exists(output_path):
        try:
            npz_mtime = os.path.getmtime(output_path)
            existing_npz = np.load(output_path)
            existing_keys = set(
                zip(
                    existing_npz["article_ids"].tolist(),
                    existing_npz["tile_indices"].tolist(),
                    existing_npz["chunk_indices"].tolist(),
                )
            )
            before = len(tile_infos)

            # Partition tile_infos into: new (not in npz) + updated (in npz but file is newer)
            new_infos = []
            for ti in tile_infos:
                key = (
                    ti.article_id,
                    ti.tile_index,
                    ti.chunk_index if hasattr(ti, "chunk_index") else 0,
                )
                if key not in existing_keys:
                    new_infos.append(ti)
                else:
                    # Check mtime — if chunk file is newer than npz, re-embed it
                    chunk_path = (
                        ti.chunk_path
                        if hasattr(ti, "chunk_path")
                        else getattr(ti, "tile_path", None)
                    )
                    if chunk_path and os.path.getmtime(chunk_path) > npz_mtime:
                        new_infos.append(ti)
                        stale_keys.add(key)

            tile_infos = new_infos
            logger.info(
                "Incremental: %d existing, %d new, %d updated (was %d total) in %s",
                len(existing_keys),
                len(tile_infos) - len(stale_keys),
                len(stale_keys),
                before,
                shard_name,
            )
            if not tile_infos:
                logger.info(
                    "Shard %d: all %d chunks up to date, skipping",
                    shard_id,
                    len(existing_keys),
                )
                return {
                    "shard_dir": shard_dir,
                    "output_path": output_path,
                    "num_tiles": len(existing_keys),
                    "num_articles": len(set(existing_npz["article_ids"].tolist())),
                    "elapsed_s": time.time() - t0,
                }
        except Exception as e:
            logger.warning(
                "Could not load existing %s for incremental: %s", output_path, e
            )
            existing_npz = None

    num_gpus = len(gpu_ids)
    if num_gpus == 1:
        # Single GPU — run in-process (no multiprocessing overhead)
        partial_path = gpu_worker(
            gpu_ids[0],
            tile_infos,
            model,
            batch_size,
            output_dir,
            backend,
            io_workers=io_workers,
            compress_npz=compress_npz,
            max_pixels=max_pixels,
            chunk_height=chunk_height,
            enforce_eager=enforce_eager,
            adapter_path=adapter_path,
        )
        partial_paths = [partial_path] if partial_path else []
    else:
        if reuse_workers:
            # Dynamic distribution — workers pull from shared queue
            logger.info(
                "Multi-GPU dynamic: %d tiles across %d GPUs", len(tile_infos), num_gpus
            )
            partial_paths = run_gpu_workers_parallel(
                per_gpu=None,
                gpu_ids=gpu_ids,
                model_path=model,
                batch_size=batch_size,
                result_dir=output_dir,
                backend=backend,
                io_workers=io_workers,
                compress_npz=compress_npz,
                reuse_workers=True,
                max_pixels=max_pixels,
                chunk_height=chunk_height,
                enforce_eager=enforce_eager,
                tile_infos=tile_infos,
                adapter_path=adapter_path,
            )
        else:
            # Static split — round-robin by article
            article_ids = sorted(set(t.article_id for t in tile_infos))
            gpu_assignment: dict[int, int] = {}
            for i, aid in enumerate(article_ids):
                gpu_assignment[aid] = gpu_ids[i % num_gpus]

            per_gpu: dict[int, list[TileInfo]] = {gid: [] for gid in gpu_ids}
            for ti in tile_infos:
                per_gpu[gpu_assignment[ti.article_id]].append(ti)

            for gid, tiles in per_gpu.items():
                logger.info(
                    "GPU %d: assigned %d tiles from %d articles",
                    gid,
                    len(tiles),
                    len({t.article_id for t in tiles}),
                )

            partial_paths = run_gpu_workers_parallel(
                per_gpu=per_gpu,
                gpu_ids=gpu_ids,
                model_path=model,
                batch_size=batch_size,
                result_dir=output_dir,
                backend=backend,
                io_workers=io_workers,
                compress_npz=compress_npz,
                reuse_workers=False,
                max_pixels=max_pixels,
                chunk_height=chunk_height,
                enforce_eager=enforce_eager,
                adapter_path=adapter_path,
            )

    # Merge partial results into final .npz
    if not partial_paths:
        logger.error("No partial results produced for %s", shard_dir)
        return {
            "shard_dir": shard_dir,
            "output_path": "",
            "num_tiles": 0,
            "num_articles": 0,
            "elapsed_s": time.time() - t0,
        }

    is_chunk_mode = mode == "chunks"
    all_emb, all_aids, all_tidx = [], [], []
    all_cidx, all_yo = [], []
    all_ph, all_vw, all_th = [], [], []
    all_ih, all_tp = [], []

    # Prepend existing data for incremental merge (excluding stale entries)
    if existing_npz is not None:
        if stale_keys:
            # Build mask: keep rows whose key is NOT in stale_keys
            ex_aids = existing_npz["article_ids"]
            ex_tidx = existing_npz["tile_indices"]
            ex_cidx = existing_npz["chunk_indices"]
            keep_mask = np.array(
                [
                    (int(ex_aids[j]), int(ex_tidx[j]), int(ex_cidx[j]))
                    not in stale_keys
                    for j in range(len(ex_aids))
                ],
                dtype=bool,
            )
            logger.info(
                "Incremental merge: keeping %d/%d existing rows (%d stale replaced)",
                keep_mask.sum(),
                len(keep_mask),
                len(stale_keys),
            )
            all_emb.append(existing_npz["embeddings"][keep_mask])
            all_aids.append(ex_aids[keep_mask])
            all_tidx.append(ex_tidx[keep_mask])
            all_cidx.append(ex_cidx[keep_mask])
            all_ph.append(existing_npz["page_heights"][keep_mask])
            all_vw.append(existing_npz["viewport_widths"][keep_mask])
            all_th.append(existing_npz["tile_heights"][keep_mask])
            all_ih.append(existing_npz["image_hashes"][keep_mask])
            all_tp.append(existing_npz["tile_paths"][keep_mask])
            if is_chunk_mode and "y_offsets" in existing_npz:
                all_yo.append(existing_npz["y_offsets"][keep_mask])
        else:
            all_emb.append(existing_npz["embeddings"])
            all_aids.append(existing_npz["article_ids"])
            all_tidx.append(existing_npz["tile_indices"])
            all_cidx.append(existing_npz["chunk_indices"])
            all_ph.append(existing_npz["page_heights"])
            all_vw.append(existing_npz["viewport_widths"])
            all_th.append(existing_npz["tile_heights"])
            all_ih.append(existing_npz["image_hashes"])
            all_tp.append(existing_npz["tile_paths"])
            if is_chunk_mode and "y_offsets" in existing_npz:
                all_yo.append(existing_npz["y_offsets"])

    # Deduplicate partial paths: persistent workers overwrite the same
    # partial_gpu{id}.npz for each work item, so the same file may appear
    # multiple times in partial_paths.  Reading it more than once duplicates
    # every embedding in the final .npz.
    seen_pp: set[str] = set()
    unique_partial_paths = []
    for pp in partial_paths:
        rp = os.path.realpath(pp)
        if rp not in seen_pp:
            seen_pp.add(rp)
            unique_partial_paths.append(pp)
    if len(unique_partial_paths) < len(partial_paths):
        logger.info(
            "Deduplicated partial paths: %d -> %d unique",
            len(partial_paths),
            len(unique_partial_paths),
        )

    for pp in unique_partial_paths:
        data = np.load(pp)
        all_emb.append(data["embeddings"])
        all_aids.append(data["article_ids"])
        all_tidx.append(data["tile_indices"])
        all_cidx.append(data["chunk_indices"])
        all_ph.append(data["page_heights"])
        all_vw.append(data["viewport_widths"])
        all_th.append(data["tile_heights"])
        all_ih.append(data["image_hashes"])
        all_tp.append(data["tile_paths"])
        if is_chunk_mode and "y_offsets" in data:
            all_yo.append(data["y_offsets"])

    embeddings = np.concatenate(all_emb, axis=0)
    article_ids = np.concatenate(all_aids)
    tile_indices = np.concatenate(all_tidx)
    chunk_indices = np.concatenate(all_cidx)
    page_heights = np.concatenate(all_ph)
    viewport_widths = np.concatenate(all_vw)
    tile_heights = np.concatenate(all_th)
    image_hashes = np.concatenate(all_ih)
    tile_paths = np.concatenate(all_tp)

    if is_chunk_mode:
        y_offsets = (
            np.concatenate(all_yo)
            if all_yo
            else np.zeros(len(embeddings), dtype=np.int32)
        )
        # Sort by (article_id, tile_index, chunk_index)
        sort_idx = np.lexsort((chunk_indices, tile_indices, article_ids))
    else:
        # Sort by (article_id, tile_index)
        sort_idx = np.lexsort((tile_indices, article_ids))

    embeddings = embeddings[sort_idx]
    article_ids = article_ids[sort_idx]
    tile_indices = tile_indices[sort_idx]
    chunk_indices = chunk_indices[sort_idx]
    page_heights = page_heights[sort_idx]
    viewport_widths = viewport_widths[sort_idx]
    tile_heights = tile_heights[sort_idx]
    image_hashes = image_hashes[sort_idx]
    tile_paths = tile_paths[sort_idx]

    extra_arrays = {}
    if is_chunk_mode:
        y_offsets = y_offsets[sort_idx]
        extra_arrays["y_offsets"] = y_offsets

    output_path = os.path.join(output_dir, f"shard_{shard_id:03d}.npz")
    save_npz(
        output_path,
        compressed=compress_npz,
        embeddings=embeddings,
        article_ids=article_ids,
        tile_indices=tile_indices,
        chunk_indices=chunk_indices,
        page_heights=page_heights,
        viewport_widths=viewport_widths,
        tile_heights=tile_heights,
        image_hashes=image_hashes,
        tile_paths=tile_paths,
        shard_id=np.int32(shard_id),
        **extra_arrays,
    )

    # Clean up partial files
    for pp in unique_partial_paths:
        try:
            os.remove(pp)
        except OSError:
            pass

    elapsed = time.time() - t0
    num_articles = len(set(article_ids.tolist()))
    logger.info(
        "Shard %d: %d embeddings (%d articles) in %.1fs -> %s",
        shard_id,
        len(embeddings),
        num_articles,
        elapsed,
        output_path,
    )

    return {
        "shard_dir": shard_dir,
        "output_path": output_path,
        "num_tiles": len(embeddings),
        "num_articles": num_articles,
        "elapsed_s": elapsed,
    }
