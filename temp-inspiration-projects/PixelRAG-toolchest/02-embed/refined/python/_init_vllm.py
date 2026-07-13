def _init_vllm(model_path: str, gpu_id: int, enforce_eager: bool = False):
    """Initialize vLLM embedding engine on a single GPU."""
    from vllm import LLM, EngineArgs
    from vllm.config import PoolerConfig

    llm = LLM(
        **vars(
            EngineArgs(
                model=model_path,
                runner="pooling",
                dtype="bfloat16",
                trust_remote_code=True,
                max_model_len=4096,
                enforce_eager=enforce_eager,
                pooler_config=PoolerConfig(pooling_type="LAST"),
            )
        )
    )
    return llm
