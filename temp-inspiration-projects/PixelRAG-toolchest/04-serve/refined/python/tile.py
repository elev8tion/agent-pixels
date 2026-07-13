@app.get("/tile")
async def tile(path: str):
    """Serve a tile image by its local path (legacy, use /tile/{article_id}/{tile_index}/{chunk_index} instead)."""
    tiles_dir = _state.get("tiles_dir", "./tiles")
    resolved = os.path.realpath(path)
    if not resolved.startswith(os.path.realpath(tiles_dir)):
        raise HTTPException(status_code=403, detail="Path not under tiles directory")
    if not os.path.isfile(resolved):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(resolved, media_type="image/png")
