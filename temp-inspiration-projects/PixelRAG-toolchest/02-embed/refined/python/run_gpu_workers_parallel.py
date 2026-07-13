def run_gpu_workers_parallel(
    per_gpu: dict[int, list[TileInfo]] | None,
    gpu_ids: list[int],
    model_path: str,
    batch_size: int,
    result_dir: str,
    backend: str,
    io_workers: int,
    compress_npz: bool,
    reuse_workers: bool = False,
    max_pixels: int | None = None,
    chunk_height: int | None = None,
    enforce_eager: bool = False,
    tile_infos: list[TileInfo] | None = None,
    adapter_path: str | None = None,
) -> list[str]:
    """Launch one non-daemonic process per GPU and collect partial .npz paths.

    When reuse_workers=True, uses dynamic work distribution via a shared queue.
    Pass tile_infos directly (per_gpu is ignored). Workers pull work chunks
    dynamically, so fast GPUs process more.

    When reuse_workers=False, uses static per_gpu assignment with one-shot processes.
    """
    if reuse_workers:
        # Dynamic distribution: pass all tiles, workers pull from shared queue
        all_tiles = tile_infos if tile_infos is not None else []
        if not all_tiles and per_gpu:
            # Fallback: flatten per_gpu into single list
            for tiles in per_gpu.values():
                all_tiles.extend(tiles)

        key = (
            tuple(gpu_ids),
            model_path,
            backend,
            io_workers,
            bool(compress_npz),
            max_pixels,
            chunk_height,
            enforce_eager,
            adapter_path,
        )
        pool = _PERSISTENT_POOLS.get(key)
        if pool is None:
            pool = PersistentGpuWorkerPool(
                gpu_ids=gpu_ids,
                model_path=model_path,
                backend=backend,
                io_workers=io_workers,
                compress_npz=compress_npz,
                max_pixels=max_pixels,
                chunk_height=chunk_height,
                enforce_eager=enforce_eager,
                adapter_path=adapter_path,
            )
            _PERSISTENT_POOLS[key] = pool
        return pool.run(
            tile_infos=all_tiles, batch_size=batch_size, result_dir=result_dir
        )

    import torch.multiprocessing as mp

    ctx = mp.get_context("spawn")
    result_queue = ctx.Queue()
    procs: list[tuple[int, "mp.Process"]] = []

    # Count active GPUs first to size the barrier correctly.
    active_gids = [gid for gid in gpu_ids if per_gpu.get(gid)]
    init_barrier = ctx.Barrier(len(active_gids)) if len(active_gids) > 1 else None

    for gid in active_gids:
        tiles = per_gpu[gid]
        p = ctx.Process(
            target=_gpu_worker_entry,
            args=(
                result_queue,
                gid,
                tiles,
                model_path,
                batch_size,
                result_dir,
                backend,
                io_workers,
                compress_npz,
                max_pixels,
                chunk_height,
                enforce_eager,
                init_barrier,
                adapter_path,
            ),
            daemon=False,
        )
        p.start()
        procs.append((gid, p))

    expected = len(procs)
    results: dict[int, dict] = {}
    while len(results) < expected:
        try:
            res = result_queue.get(timeout=5)
            results[res["gpu_id"]] = res
        except queue.Empty:
            if all(not p.is_alive() for _gid, p in procs):
                break

    for _gid, p in procs:
        p.join()

    errors: list[str] = []
    partial_paths: list[str] = []
    for gid, p in procs:
        res = results.get(gid)
        if res is None:
            msg = f"GPU {gid}: no result reported (exitcode={p.exitcode})"
            logger.error(msg)
            errors.append(msg)
            continue
        if res.get("error"):
            msg = f"GPU {gid} failed:\n{res['error']}"
            logger.error(msg)
            errors.append(msg)
            continue
        partial_path = res.get("partial_path", "")
        if partial_path:
            partial_paths.append(partial_path)
        if p.exitcode not in (0, None):
            errors.append(f"GPU {gid}: worker exited with code {p.exitcode}")

    if errors:
        logger.error("Multi-GPU worker failures:\n%s", "\n".join(errors))
        if not partial_paths:
            raise RuntimeError("All GPU workers failed:\n" + "\n".join(errors))
        logger.warning(
            "%d/%d GPU workers failed, continuing with %d partial results",
            len(errors),
            len(procs),
            len(partial_paths),
        )

    return partial_paths
