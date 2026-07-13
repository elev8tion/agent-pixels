class VectorRetriever(BaseRetriever):
    """Retrieve similar screenshots using vector similarity search.

    Uses Jina API for embedding and retrieval across dataset screenshots only.
    """

    def __init__(
        self,
        api_key: str,
        screenshot_dir: str = "screenshots",
        cache_path: str | None = None,
        use_multivector: bool = True,
        top_k: int = 3,
        examples: list[dict] | None = None,
    ):
        self.top_k = top_k
        self.screenshot_dir = screenshot_dir
        self.examples = examples or []
        os.makedirs(screenshot_dir, exist_ok=True)

        # Prepare missing screenshots and get file paths
        screenshot_paths = self._prepare_screenshots()

        # Import retrieval system
        try:
            from scripts.jina_retrieval import JinaAPIRetrievalSystem
        except ImportError:
            try:
                from jina_retrieval import JinaAPIRetrievalSystem
            except ImportError:
                raise ImportError("JinaAPIRetrievalSystem not available")

        vector_type = "single vector" if not use_multivector else "multivector"
        logger.info(f"Initializing VectorRetriever with {vector_type} mode")

        self.retrieval_system = JinaAPIRetrievalSystem(
            api_key=api_key,
            use_multivector=use_multivector,
            device="cpu",  # Use CPU to avoid OOM when VLM is on GPU
        )
        # Only embed screenshots for current dataset
        self.retrieval_system.embed_images(
            file_paths=screenshot_paths, cache_path=cache_path
        )
        logger.info(
            f"VectorRetriever ready with {len(self.retrieval_system.image_paths)} images"
        )

    def _prepare_screenshots(self) -> list[str]:
        """Prepare screenshots for dataset and return list of paths."""
        from .simpleqa_data import capture_screenshot_for_example

        screenshot_paths = []
        missing = []

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

        if missing:
            logger.info(
                f"Found {len(missing)} missing screenshots out of {len(self.examples)} total examples"
            )
            logger.info(f"Preparing {len(missing)} missing screenshots...")
            # Use a more robust approach: continue even if some screenshots fail
            success_count = 0
            for ex in missing:
                try:
                    capture_screenshot_for_example(ex, self.screenshot_dir)
                    success_count += 1
                except Exception as e:
                    logger.warning(
                        f"Failed to capture screenshot for {ex.get('id', 'unknown')}: {e}"
                    )
                    # Continue with next screenshot instead of failing completely
            logger.info(
                f"Screenshots prepared: {success_count}/{len(missing)} successful"
            )
        else:
            logger.info(
                f"All {len(self.examples)} screenshots already exist, skipping preparation"
            )

        # Return only existing screenshots
        return [
            p for p in screenshot_paths if os.path.exists(p) and os.path.getsize(p) > 0
        ]

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        loop = asyncio.get_event_loop()

        try:
            results = await loop.run_in_executor(
                None, self.retrieval_system.retrieve, query, self.top_k
            )

            if results:
                return RetrievalResult(images=results, retrieval_type="vector")
        except Exception as e:
            logger.warning(f"Vector retrieval failed: {e}")

        return RetrievalResult(retrieval_type="vector")
