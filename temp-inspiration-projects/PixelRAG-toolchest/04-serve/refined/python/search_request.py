class SearchRequest(BaseModel):
    queries: list[Query]
    n_docs: int = 10
    nprobe: int | None = None  # override default nprobe
    min_tile_height: int | None = None  # filter out small/blank chunks
    instruction: str | None = None  # override query embedding instruction
    include_images: bool = False  # return base64-encoded tile images
    articles_only: bool = False  # drop Wikipedia meta pages (Portal:, List_of_, …)
