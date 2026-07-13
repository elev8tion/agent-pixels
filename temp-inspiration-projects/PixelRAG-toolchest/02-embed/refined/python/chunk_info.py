class ChunkInfo(NamedTuple):
    """Metadata for a single chunk image (1024px strip of a tile)."""

    article_id: int
    tile_index: int
    chunk_index: int
    chunk_path: str
    page_height: int
    viewport_width: int
    y_offset: int
    chunk_height: int
