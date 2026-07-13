class TiledScreenshotRetriever(BaseRetriever):
    """Use tiled screenshot from ground truth URL.

    Captures screenshot for the example's URL, splits it into tiles,
    and returns tiles. This is ground truth (not vector search).

    Args:
        max_tiles: Maximum number of tiles to return. If None, returns all tiles.
                   For context-aware limiting, calculate based on model context length.
                   Rough estimate: max_tiles = (context_length - 2000) / tokens_per_tile
                   where tokens_per_tile ≈ 1500-2000 for most VLMs.
    """

    def __init__(
        self,
        screenshot_dir: str = "screenshots",
        tiles_dir: str = "tiles",
        tile_size: int = 512,
        overlap: int = 0,
        max_tiles: int | None = None,
    ):
        self.screenshot_dir = screenshot_dir
        self.tiles_dir = tiles_dir
        self.tile_size = tile_size
        self.overlap = overlap
        self.max_tiles = max_tiles
        os.makedirs(tiles_dir, exist_ok=True)

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        from .simpleqa_data import (
            capture_screenshot_async,
            encode_screenshot_async,
            extract_url_from_metadata,
            split_image_to_tiles,
        )

        # Get or capture screenshot
        screenshot_path = await capture_screenshot_async(example, self.screenshot_dir)

        if not screenshot_path:
            return RetrievalResult(
                retrieval_type="tiled_screenshot",
                source_url=extract_url_from_metadata(example),
            )

        # Split into tiles
        example_id = example.get("id", "unknown")
        example_tiles_dir = os.path.join(self.tiles_dir, example_id)
        tile_paths = split_image_to_tiles(
            screenshot_path,
            example_tiles_dir,
            tile_size=self.tile_size,
            overlap=self.overlap,
        )

        if not tile_paths:
            # Fall back to full screenshot
            base64_image = await encode_screenshot_async(screenshot_path)
            return RetrievalResult(
                base64_image=base64_image,
                source_url=extract_url_from_metadata(example),
                retrieval_type="tiled_screenshot",
            )

        # Limit tiles if max_tiles is set
        if self.max_tiles is not None and len(tile_paths) > self.max_tiles:
            logger.info(f"Limiting tiles from {len(tile_paths)} to {self.max_tiles}")
            tile_paths = tile_paths[: self.max_tiles]

        # Return tiles as images list (path, score=1.0 for ground truth)
        images = [(path, 1.0) for path in tile_paths]

        return RetrievalResult(
            images=images,
            source_url=extract_url_from_metadata(example),
            retrieval_type="tiled_screenshot",
        )
