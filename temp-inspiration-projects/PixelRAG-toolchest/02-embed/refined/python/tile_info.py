class TileInfo(NamedTuple):
    """Metadata for a single tile image (or a chunk of one)."""

    article_id: int
    tile_index: int
    tile_path: str
    page_height: int
    viewport_width: int
    tile_height: int
    chunk_index: int = 0  # 0 = whole tile or first chunk
