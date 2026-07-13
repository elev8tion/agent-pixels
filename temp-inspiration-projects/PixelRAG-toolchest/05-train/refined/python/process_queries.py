def process_queries(processor, queries):
    """Wrap queries in chat template with retrieval instruction."""
    texts = [_QUERY_PREFIX + q + _QUERY_SUFFIX for q in queries]
    return processor(text=texts, return_tensors="pt", padding="longest")
