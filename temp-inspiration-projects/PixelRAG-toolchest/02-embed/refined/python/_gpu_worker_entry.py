def _gpu_worker_entry(
    result_queue,
    gpu_id: int,
    tile_infos: list[TileInfo],
    model_path: str,
    batch_size: int,
    result_dir: str,
    backend: str,
    io_workers: int,
    compress_npz: bool,
    max_pixels: int | None = None,
    chunk_height: int | None = None,
    enforce_eager: bool = False,
    init_barrier=None,
    adapter_path: str | None = None,
) -> None:
    """Run gpu_worker in a subprocess and report result via queue."""
    try:
        partial_path = gpu_worker(
            gpu_id=gpu_id,
            tile_infos=tile_infos,
            model_path=model_path,
            batch_size=batch_size,
            result_dir=result_dir,
            backend=backend,
            io_workers=io_workers,
            compress_npz=compress_npz,
            max_pixels=max_pixels,
            chunk_height=chunk_height,
            enforce_eager=enforce_eager,
            init_barrier=init_barrier,
            adapter_path=adapter_path,
        )
        result_queue.put(
            {
                "gpu_id": gpu_id,
                "partial_path": partial_path,
                "error": "",
            }
        )
    except Exception:
        result_queue.put(
            {
                "gpu_id": gpu_id,
                "partial_path": "",
                "error": traceback.format_exc(),
            }
        )
