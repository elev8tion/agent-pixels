class LocalWikiTiledScreenshotRetriever(BaseRetriever):
    """Ground-truth tiled retriever using pre-rendered Wikipedia tiles from local kiwix.

    For each example, looks up the Wikipedia URL in the local kiwix tile store,
    copies raw tiles to a local cache, cuts into tile_height strips, and passes
    all tiles to the VLM as context. No Selenium, no SSH.

    Args:
        tiles_dir: Directory for cut tile strips (output).
        wiki_cache_dir: Directory for raw kiwix tile copies.
        tile_height: Height of each strip in pixels (default 1024).
        max_tiles: Maximum tiles to pass to VLM (None = all).
    """

    def __init__(
        self,
        tiles_dir: str = "tiles-local-wiki",
        wiki_cache_dir: str = "screenshots-localwiki",
        tile_height: int = 1024,
        max_tiles: int | None = None,
    ):
        self.tiles_dir = tiles_dir
        self.wiki_cache_dir = wiki_cache_dir
        self.tile_height = tile_height
        self.max_tiles = max_tiles
        os.makedirs(tiles_dir, exist_ok=True)
        os.makedirs(wiki_cache_dir, exist_ok=True)

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        from .simpleqa_data import extract_url_from_metadata

        ex_id = example.get("id", "unknown")
        url = extract_url_from_metadata(example) or ""

        loop = asyncio.get_event_loop()
        try:
            tile_paths = await loop.run_in_executor(
                None,
                lambda: _lookup_and_copy_local_wiki_tiles(
                    ex_id, url, self.tiles_dir, self.wiki_cache_dir, self.tile_height
                ),
            )
        except RuntimeError as e:
            logger.error(f"local-wiki [{ex_id}]: {e}")
            return RetrievalResult(retrieval_type="local_wiki_tiled", source_url=url)

        if self.max_tiles is not None and len(tile_paths) > self.max_tiles:
            tile_paths = tile_paths[: self.max_tiles]

        images = [(path, 1.0) for path in tile_paths]
        return RetrievalResult(
            images=images,
            source_url=url,
            retrieval_type="local_wiki_tiled",
        )
