def _image_path(ti: "TileInfo | ChunkInfo") -> str:
    """Return the image file path regardless of info type."""
    return ti.tile_path if isinstance(ti, TileInfo) else ti.chunk_path
