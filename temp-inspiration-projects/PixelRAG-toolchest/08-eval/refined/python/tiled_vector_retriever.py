class TiledVectorRetriever(BaseRetriever):
    """Retrieve similar image tiles using vector similarity search.

    Splits dataset screenshots into fixed-size tiles, embeds each tile,
    and retrieves the most relevant tiles for a query.
    """

    def __init__(
        self,
        api_key: str,
        screenshot_dir: str = "screenshots",
        tiles_dir: str = "tiles",
        tile_size: int = 512,
        overlap: int = 0,
        cache_path: str | None = None,
        use_multivector: bool = True,
        top_k: int = 3,
        examples: list[dict] | None = None,
    ):
        self.top_k = top_k
        self.screenshot_dir = screenshot_dir
        self.tiles_dir = tiles_dir
        self.tile_size = tile_size
        self.overlap = overlap
        self.examples = examples or []
        os.makedirs(screenshot_dir, exist_ok=True)
        os.makedirs(tiles_dir, exist_ok=True)

        # Build example_id -> URL mapping (prioritize Wikipedia URLs)
        from .simpleqa_data import extract_url_from_metadata

        self.id_to_url = {}
        for ex in self.examples:
            ex_id = ex.get("id", "")
            url = extract_url_from_metadata(ex)  # Uses Wikipedia-first priority
            if url:
                self.id_to_url[ex_id] = url

        # Prepare screenshots and get tile paths
        tile_paths = self._prepare_screenshots_and_tiles()

        # Import retrieval system
        try:
            from scripts.jina_retrieval import JinaAPIRetrievalSystem
        except ImportError:
            try:
                from jina_retrieval import JinaAPIRetrievalSystem
            except ImportError:
                raise ImportError("JinaAPIRetrievalSystem not available")

        vector_type = "single vector" if not use_multivector else "multivector"
        logger.info(f"Initializing TiledVectorRetriever with {vector_type} mode")

        self.retrieval_system = JinaAPIRetrievalSystem(
            api_key=api_key,
            use_multivector=use_multivector,
            device="cpu",  # Use CPU to avoid OOM when VLM is on GPU
        )
        # Only embed tiles for current dataset
        self.retrieval_system.embed_images(file_paths=tile_paths, cache_path=cache_path)
        logger.info(
            f"TiledVectorRetriever ready with {len(self.retrieval_system.image_paths)} tiles"
        )

    def _prepare_screenshots_and_tiles(self) -> list[str]:
        """Prepare screenshots and tiles for dataset, return tile paths."""
        from .simpleqa_data import capture_screenshot_for_example, split_image_to_tiles
        from tqdm import tqdm

        screenshot_paths = []
        missing = []

        # Collect screenshot paths and identify missing
        for ex in self.examples:
            screenshot_path = os.path.join(
                self.screenshot_dir, f"{ex['id']}_fullhd.png"
            )
            screenshot_paths.append(screenshot_path)
            if (
                not os.path.exists(screenshot_path)
                or os.path.getsize(screenshot_path) == 0
            ):
                missing.append(ex)

        # Capture missing screenshots
        if missing:
            logger.info(f"Preparing {len(missing)} missing screenshots...")
            for ex in tqdm(missing, desc="Capturing screenshots"):
                capture_screenshot_for_example(ex, self.screenshot_dir)
            logger.info("Screenshots prepared.")

        # Split each screenshot into tiles
        all_tile_paths = []
        logger.info(
            f"Splitting {len(screenshot_paths)} screenshots into tiles (output: {self.tiles_dir})..."
        )
        for screenshot_path in tqdm(screenshot_paths, desc="Splitting tiles"):
            if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
                tile_paths = split_image_to_tiles(
                    screenshot_path, self.tiles_dir, self.tile_size, self.overlap
                )
                all_tile_paths.extend(tile_paths)

        # Filter out tiles with extreme aspect ratios
        filtered_tile_paths = _filter_tiles_by_aspect_ratio(all_tile_paths)
        logger.info(
            f"Prepared {len(filtered_tile_paths)} tiles from {len(screenshot_paths)} screenshots (filtered {len(all_tile_paths) - len(filtered_tile_paths)} extreme aspect ratio tiles)"
        )
        return filtered_tile_paths

    def _extract_urls_from_results(self, results: list) -> str:
        """Extract source URLs from tile paths in results, preserving retrieval order."""
        urls = []
        seen = set()
        for item in results:
            # item is (path, score) tuple
            path = item[0] if isinstance(item, tuple) else item
            # Extract example_id from tile path: {example_id}_fullhd_tile_{x}_{y}.png
            filename = os.path.basename(path)
            # Split by _fullhd_ or just get the first part before _tile_
            if "_tile_" in filename:
                example_id = filename.split("_tile_")[0]
                # Remove _fullhd suffix if present
                if example_id.endswith("_fullhd"):
                    example_id = example_id[:-7]
                if example_id in self.id_to_url:
                    url = self.id_to_url[example_id]
                    if url not in seen:
                        seen.add(url)
                        urls.append(url)
        return ", ".join(urls)

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        del example  # Not used - retrieval is from pre-built index
        loop = asyncio.get_event_loop()

        try:
            results = await loop.run_in_executor(
                None, self.retrieval_system.retrieve, query, self.top_k
            )

            if results:
                source_url = self._extract_urls_from_results(results)
                return RetrievalResult(
                    images=results, source_url=source_url, retrieval_type="tiled_vector"
                )
        except Exception as e:
            logger.warning(f"Tiled vector retrieval failed: {e}")

        return RetrievalResult(retrieval_type="tiled_vector")
