def gpu_worker(
    gpu_id: int,
    tile_infos: list[TileInfo],
    model_path: str,
    batch_size: int,
    result_dir: str,
    backend: str = "vllm",
    io_workers: int = 8,
    compress_npz: bool = False,
    max_pixels: int | None = None,
    chunk_height: int | None = None,
    enforce_eager: bool = False,
    init_barrier=None,
    adapter_path: str | None = None,
) -> str:
    """Load model on one GPU, embed all assigned tiles, write partial .npz.

    This function runs in a child process with CUDA_VISIBLE_DEVICES set.

    Args:
        gpu_id: Physical GPU ID.
        tile_infos: Tiles assigned to this GPU.
        model_path: HuggingFace model name or local path.
        batch_size: Tiles per embed call.
        result_dir: Directory to write partial result file.
        backend: "vllm" or "sglang".
        init_barrier: If provided, wait here after model load so all GPUs
            finish CUDA graph capture before any starts embedding.  Avoids
            concurrent-capture stalls on some GPUs (observed on GPU 6/vLLM).

    Returns:
        Path to the partial .npz file written by this worker.
    """
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    os.environ.setdefault("SGLANG_LOG_LEVEL", "error")

    init_fn, get_tok_fn, embed_fn = BACKENDS[backend]

    logger.info(
        "GPU %d: loading model %s via %s (%d tiles)",
        gpu_id,
        model_path,
        backend,
        len(tile_infos),
    )
    t0 = time.time()

    # Pass adapter_path only for direct_gpu (other backends don't support it)
    if adapter_path and backend == "direct_gpu":
        engine = init_fn(
            model_path, gpu_id, enforce_eager=enforce_eager, adapter_path=adapter_path
        )
    else:
        engine = init_fn(model_path, gpu_id, enforce_eager=enforce_eager)

    dt = time.time() - t0
    logger.info("GPU %d: model loaded in %.1fs", gpu_id, dt)

    # Wait for all GPUs to finish init (CUDA graph capture) before embedding.
    if init_barrier is not None:
        try:
            init_barrier.wait(timeout=120)
            logger.info("GPU %d: all workers ready, starting embed", gpu_id)
        except threading.BrokenBarrierError:
            logger.error(
                "GPU %d: barrier broken (another GPU failed to init), continuing anyway",
                gpu_id,
            )

    def _cleanup_engine() -> None:
        shutdown = getattr(engine, "shutdown", None)
        if callable(shutdown):
            try:
                shutdown()
            except Exception as e:
                logger.warning("GPU %d: engine shutdown failed: %s", gpu_id, e)

    # Build prompt via chat template (official Qwen3-VL-Embedding format)
    tokenizer = get_tok_fn(engine)
    prompt = _build_chat_prompt(tokenizer)
    logger.info("GPU %d: prompt template: %s", gpu_id, repr(prompt[:120]))

    partial_path = _embed_tile_infos_with_engine(
        engine=engine,
        gpu_id=gpu_id,
        tile_infos=tile_infos,
        batch_size=batch_size,
        result_dir=result_dir,
        embed_fn=embed_fn,
        prompt=prompt,
        io_workers=io_workers,
        compress_npz=compress_npz,
        max_pixels=max_pixels,
        chunk_height=chunk_height,
    )
    _cleanup_engine()
    return partial_path
