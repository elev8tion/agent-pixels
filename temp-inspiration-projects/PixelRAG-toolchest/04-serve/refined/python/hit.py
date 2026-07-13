class Hit(BaseModel):
    score: float
    vector_id: int
    article_id: int
    tile_index: int
    chunk_index: int
    y_offset: int
    tile_height: int
    path: str
    url: str
    # Which (tile, chunk) coordinates actually exist on disk for this article,
    # e.g. "0:0-8,1:0-4" — lets agents page through an article without
    # guessing coordinates past its end.
    article_pages: str | None = None
    image_base64: str | None = None
