@app.post("/reconstruct")
async def reconstruct(req: ReconstructRequest):
    """Reconstruct stored embeddings by vector_id (for alignment debugging)."""
    index = _state["index"]
    # Ensure direct map exists for reconstruct
    if not hasattr(index, "_direct_map_built"):
        index.make_direct_map()
        index._direct_map_built = True
    vecs = []
    for vid in req.vector_ids:
        vecs.append(index.reconstruct(vid).tolist())
    return {"embeddings": vecs}
