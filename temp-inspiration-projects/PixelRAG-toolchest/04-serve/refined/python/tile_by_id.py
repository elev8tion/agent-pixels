@app.get("/tile/{article_id}/{tile_index}/{chunk_index}")
async def tile_by_id(article_id: int, tile_index: int, chunk_index: int):
    """Serve a tile image by article_id, tile_index, chunk_index."""
    path = _resolve_path(article_id, tile_index, chunk_index)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Tile not found")
    return FileResponse(path, media_type="image/png")
