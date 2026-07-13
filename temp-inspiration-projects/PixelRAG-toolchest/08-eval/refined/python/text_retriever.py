class TextRetriever(BaseRetriever):
    """Use text content fetched from URL.

    Can use pre-cached text or fetch on demand.
    """

    def __init__(
        self,
        max_chars: int = 50000,
        text_cache: dict | None = None,
        cache_path: str | None = None,
    ):
        self.max_chars = max_chars
        self.text_cache = text_cache
        self.cache_path = cache_path
        self._cache_lock = asyncio.Lock()

    async def _save_to_cache(self, example_id: str, text: str, url: str):
        """Append result to cache file."""
        if not self.cache_path:
            return
        try:
            import json

            async with self._cache_lock:
                with open(self.cache_path, "a") as f:
                    cache_entry = {"id": example_id, "text": text, "url": url}
                    f.write(json.dumps(cache_entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to save to cache: {e}")

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        from .simpleqa_data import fetch_text_async

        example_id = example.get("id", "")
        was_cached = self.text_cache and example_id in self.text_cache

        text, source_url = await fetch_text_async(
            example, self.max_chars, self.text_cache
        )

        # Save to cache if not already cached
        if not was_cached and text and source_url:
            await self._save_to_cache(example_id, text, source_url)

        return RetrievalResult(
            text=text, source_url=source_url, retrieval_type="text_rag"
        )
