def _get_tokenizer_direct_gpu(engine):
    _, processor = engine
    return processor.tokenizer
