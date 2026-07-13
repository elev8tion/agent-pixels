def _gpu_worker_persistent_entry(
    work_queue,
    result_queue,
    gpu_id: int,
    model_path: str,
    backend: str,
    io_workers: int,
    compress_npz: bool,
    max_pixels: int | None = None,
    chunk_height: int | None = None,
    enforce_eager: bool = False,
    init_barrier=None,
    adapter_path: str | None = None,
) -> None:
    """Persistent GPU worker: load model once, pull work dynamically from shared queue.

    Protocol:
        - Work items: dict with "task_id", "tile_infos", "batch_size", "result_dir"
        - Round sentinel: dict with "task_id"=None, "round_id" — worker sends round_done and continues
        - Shutdown: None — worker exits
    """
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    os.environ.setdefault("SGLANG_LOG_LEVEL", "error")
    init_fn, get_tok_fn, embed_fn = BACKENDS[backend]

    engine = None
    try:
        if adapter_path and backend == "direct_gpu":
            engine = init_fn(
                model_path,
                gpu_id,
                enforce_eager=enforce_eager,
                adapter_path=adapter_path,
            )
        else:
            engine = init_fn(model_path, gpu_id, enforce_eager=enforce_eager)
        if init_barrier is not None:
            try:
                init_barrier.wait(timeout=120)
                logger.info("GPU %d: all persistent workers ready", gpu_id)
            except threading.BrokenBarrierError:
                logger.error("GPU %d: barrier broken, continuing anyway", gpu_id)
        tokenizer = get_tok_fn(engine)
        prompt = _build_chat_prompt(tokenizer)

        while True:
            task = work_queue.get()
            if task is None:
                # Shutdown signal
                break
            if task.get("task_id") is None:
                # Round-end sentinel — signal done for this round, keep looping
                result_queue.put(
                    {
                        "gpu_id": gpu_id,
                        "round_done": True,
                        "round_id": task.get("round_id"),
                    }
                )
                continue
            task_id = task["task_id"]
            try:
                partial_path = _embed_tile_infos_with_engine(
                    engine=engine,
                    gpu_id=gpu_id,
                    tile_infos=task["tile_infos"],
                    batch_size=task["batch_size"],
                    result_dir=task["result_dir"],
                    embed_fn=embed_fn,
                    prompt=prompt,
                    io_workers=io_workers,
                    compress_npz=compress_npz,
                    max_pixels=max_pixels,
                    chunk_height=chunk_height,
                    task_id=task_id,
                )
                result_queue.put(
                    {
                        "task_id": task_id,
                        "gpu_id": gpu_id,
                        "partial_path": partial_path,
                        "error": "",
                    }
                )
            except Exception:
                result_queue.put(
                    {
                        "task_id": task_id,
                        "gpu_id": gpu_id,
                        "partial_path": "",
                        "error": traceback.format_exc(),
                    }
                )
    except Exception:
        result_queue.put(
            {
                "task_id": "__init__",
                "gpu_id": gpu_id,
                "partial_path": "",
                "error": traceback.format_exc(),
            }
        )
    finally:
        if engine is not None:
            shutdown = getattr(engine, "shutdown", None)
            if callable(shutdown):
                try:
                    shutdown()
                except Exception:
                    pass
