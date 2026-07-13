def _init_sglang(model_path: str, gpu_id: int, enforce_eager: bool = False):
    """Initialize SGLang embedding engine on a single GPU.

    Key settings for vision embedding throughput on H100:
    - disable_cuda_graph: no decode phase in embedding → graphs waste memory
    - chunked_prefill_size=16384: large prefill chunks for batched vision tokens
    - max_prefill_tokens=65536: high ceiling so scheduler doesn't throttle
    - keep_mm_feature_on_device=True: avoid GPU→CPU→GPU copies of ViT features
    - mm_max_concurrent_calls=64: parallel image preprocessing
    - max_running_requests=512: pack more embedding requests
    - schedule_conservativeness=0.3: admit requests aggressively (KV freed instantly)
    - mem_fraction_static=0.80: safe with cuda graphs disabled
    - disable_radix_cache=True: embedding has no KV reuse
    """
    from sglang.srt.entrypoints.engine import Engine

    os.environ.setdefault("SGLANG_LOG_LEVEL", "error")
    return Engine(
        model_path=model_path,
        is_embedding=True,
        dtype="bfloat16",
        trust_remote_code=True,
        # Prefill tuning
        chunked_prefill_size=16384,
        max_prefill_tokens=65536,
        # Memory — no CUDA graphs frees several GB for activations
        mem_fraction_static=0.82,
        disable_radix_cache=True,
        disable_cuda_graph=True,
        # Vision
        keep_mm_feature_on_device=True,
        mm_max_concurrent_calls=64,
        # Scheduling — aggressive for embedding (no decode, KV freed instantly)
        max_running_requests=512,
        schedule_conservativeness=0.3,
    )
