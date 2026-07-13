def _normalize_query_embeddings(queries: list[Query]) -> np.ndarray:
    """Normalize externally supplied query embeddings to match service behavior."""
    if not queries:
        return np.zeros((0, _state["dimension"]), dtype=np.float32)
    if any(q.embedding is None for q in queries):
        raise HTTPException(
            status_code=400,
            detail="When using pre-computed embeddings, every query must provide `embedding`.",
        )
    if any(q.text is not None or q.image is not None for q in queries):
        raise HTTPException(
            status_code=400,
            detail="Pre-computed embeddings cannot be mixed with text/image fields in the same request.",
        )

    embeddings = np.asarray([q.embedding for q in queries], dtype=np.float32)
    if embeddings.ndim != 2:
        raise HTTPException(
            status_code=400, detail="Embeddings must have shape [batch, dim]."
        )
    expected_dim = _state["dimension"]
    if embeddings.shape[1] != expected_dim:
        raise HTTPException(
            status_code=400,
            detail=f"Embedding dim mismatch: got {embeddings.shape[1]}, expected {expected_dim}.",
        )

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / np.maximum(norms, 1e-12)
    return embeddings
