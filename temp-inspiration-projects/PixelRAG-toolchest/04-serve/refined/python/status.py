@app.get("/status", response_model=StatusResponse)
async def status():
    index = _state["index"]
    return StatusResponse(
        total_vectors=index.ntotal,
        dimension=_state["dimension"],
        nlist=_state["nlist"],
        nprobe=index.nprobe,
        model=_state["model_name"],
        index_dir=_state.get("index_dir", ""),
        tiles_dir=_state.get("tiles_dir", ""),
        index_built_at=_state["index_built_at"],
        index_size_bytes=_state["index_size_bytes"],
        metadata_size_bytes=_state["metadata_size_bytes"],
    )
