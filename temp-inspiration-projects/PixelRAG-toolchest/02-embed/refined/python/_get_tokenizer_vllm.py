def _get_tokenizer_vllm(engine):
    # vLLM API changed across versions:
    # - older: engine.llm_engine.tokenizer.tokenizer
    # - newer: engine.get_tokenizer()
    if hasattr(engine, "get_tokenizer"):
        return engine.get_tokenizer()
    return engine.llm_engine.tokenizer.tokenizer
