class ColQwenVectorRetriever(BaseRetriever):
    """Retrieve similar screenshots using ColQwen2 LEANN multi-vector retrieval."""

    def __init__(
        self,
        index_path: str,
        screenshot_dir: str = "screenshots",
        model_name: str = "colqwen2",
        search_method: str = "ann",
        first_stage_k: int = 500,
        rebuild_index: bool = False,
        recursive: bool = False,
        top_k: int = 3,
        examples: list[dict] | None = None,
        prepare_screenshots: bool = False,  # ColQwen2 doesn't need to prepare specific screenshots
    ):
        self.top_k = top_k
        self.screenshot_dir = screenshot_dir
        self.examples = examples or []
        os.makedirs(screenshot_dir, exist_ok=True)

        # Build list of image paths for the specific examples (only Wikipedia samples)
        image_paths = self._get_example_image_paths()

        if image_paths:
            logger.info(
                f"ColQwen2 will retrieve from {len(image_paths)} images for {len(self.examples)} examples"
            )
        else:
            logger.warning(
                f"No images found for examples, falling back to all images in: {screenshot_dir}"
            )

        # Import ColQwen2 retrieval system
        import sys
        from pathlib import Path

        # Add scripts directory to path for import
        scripts_dir = Path(__file__).parent.parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        try:
            from colqwen_leann_retrieval import ColQwenLEANNRetrievalSystem
        except ImportError:
            try:
                from scripts.colqwen_leann_retrieval import ColQwenLEANNRetrievalSystem
            except ImportError:
                raise ImportError(
                    "ColQwenLEANNRetrievalSystem not available. Make sure colqwen_leann_retrieval.py is in the scripts directory."
                )

        logger.info("Initializing ColQwen2 LEANN retrieval system...")
        logger.info(f"Search method: {search_method}")

        # Use filtered image paths if available, otherwise fall back to directory scanning
        if image_paths:
            self.retrieval_system = ColQwenLEANNRetrievalSystem(
                index_path=index_path,
                model_name=model_name,
                search_method=search_method,
                first_stage_k=first_stage_k,
                rebuild_index=rebuild_index,
                custom_image_paths=image_paths,  # Pass specific image paths
            )
        else:
            self.retrieval_system = ColQwenLEANNRetrievalSystem(
                index_path=index_path,
                model_name=model_name,
                search_method=search_method,
                first_stage_k=first_stage_k,
                rebuild_index=rebuild_index,
                custom_folder_path=screenshot_dir,
                custom_folder_recursive=recursive,
            )
        logger.info("ColQwen2 LEANN retrieval system ready")

    def _get_example_image_paths(self) -> list[str]:
        """Get image paths for the specific examples."""
        image_paths = []
        for ex in self.examples:
            example_id = ex.get("id", "")
            if not example_id:
                continue
            path = os.path.join(self.screenshot_dir, f"{example_id}_fullhd.png")
            if os.path.exists(path) and os.path.getsize(path) > 0:
                image_paths.append(path)
        return image_paths

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        loop = asyncio.get_event_loop()

        try:
            results = await loop.run_in_executor(
                None, self.retrieval_system.retrieve, query, self.top_k
            )

            if results:
                return RetrievalResult(images=results, retrieval_type="colqwen_vector")
        except Exception as e:
            logger.warning(f"ColQwen2 vector retrieval failed: {e}")

        return RetrievalResult(retrieval_type="colqwen_vector")
