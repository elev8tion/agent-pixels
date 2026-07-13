class JinaReaderRetriever(BaseRetriever):
    """Use Jina Reader API to fetch clean markdown text from URL.

    Jina Reader (r.jina.ai) converts any URL to LLM-friendly markdown text.
    """

    def __init__(
        self,
        max_chars: int = 50000,
        api_key: str | None = None,
        text_cache: dict | None = None,
        cache_path: str | None = None,
    ):
        self.max_chars = max_chars
        self.api_key = api_key
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
        import aiohttp
        import asyncio
        from .simpleqa_data import extract_url_from_metadata

        # Check cache first
        example_id = example.get("id", "")
        if self.text_cache and example_id in self.text_cache:
            cached = self.text_cache[example_id]
            text = cached.get("text", "")
            source_url = cached.get("url", "")
            if text:
                if len(text) > self.max_chars:
                    text = text[: self.max_chars] + "\n\n[Content truncated...]"
                return RetrievalResult(
                    text=text, source_url=source_url, retrieval_type="jina_reader"
                )

        target_url = extract_url_from_metadata(example)
        if not target_url:
            return RetrievalResult(
                text="No URL found in metadata.", retrieval_type="jina_reader"
            )

        # Use Jina Reader API with retry logic
        reader_url = f"https://r.jina.ai/{target_url}"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        max_retries = 5
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        reader_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=60),
                    ) as response:
                        # Handle rate limiting (429) with exponential backoff
                        if response.status == 429:
                            if attempt < max_retries - 1:
                                wait_time = min(2**attempt * 2, 30)  # Max 30 seconds
                                logger.warning(
                                    f"Rate limited (429) for {target_url}, waiting {wait_time}s before retry ({attempt + 1}/{max_retries})"
                                )
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                error_msg = f"Jina Reader API rate limited (429) after {max_retries} retries"
                                logger.error(f"{error_msg} for {target_url}")
                                return RetrievalResult(
                                    text=error_msg,
                                    source_url=target_url,
                                    retrieval_type="jina_reader",
                                )

                        # Handle server errors (5xx) with retry
                        if 500 <= response.status < 600:
                            if attempt < max_retries - 1:
                                wait_time = min(2**attempt, 10)  # Max 10 seconds
                                logger.warning(
                                    f"Server error ({response.status}) for {target_url}, waiting {wait_time}s before retry ({attempt + 1}/{max_retries})"
                                )
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                error_msg = (
                                    f"Jina Reader API server error: {response.status}"
                                )
                                logger.error(f"{error_msg} for {target_url}")
                                return RetrievalResult(
                                    text=error_msg,
                                    source_url=target_url,
                                    retrieval_type="jina_reader",
                                )

                        # Handle client errors (4xx) - don't retry for most
                        if response.status == 200:
                            text = await response.text()
                            # Save to cache before truncation
                            await self._save_to_cache(example_id, text, target_url)
                            # Truncate if too long
                            if len(text) > self.max_chars:
                                text = (
                                    text[: self.max_chars]
                                    + "\n\n[Content truncated...]"
                                )
                            return RetrievalResult(
                                text=text,
                                source_url=target_url,
                                retrieval_type="jina_reader",
                            )
                        else:
                            # Other 4xx errors (403, 404, etc.) - don't retry
                            error_msg = f"Jina Reader API error: {response.status}"
                            logger.warning(f"{error_msg} for {target_url}")
                            return RetrievalResult(
                                text=error_msg,
                                source_url=target_url,
                                retrieval_type="jina_reader",
                            )
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    wait_time = min(2**attempt, 10)  # Max 10 seconds
                    logger.warning(
                        f"Timeout for {target_url}, waiting {wait_time}s before retry ({attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    error_msg = f"Jina Reader fetch timeout after {max_retries} retries"
                    logger.error(f"{error_msg} for {target_url}")
                    return RetrievalResult(
                        text=error_msg,
                        source_url=target_url,
                        retrieval_type="jina_reader",
                    )
            except aiohttp.ClientError as e:
                if attempt < max_retries - 1:
                    wait_time = min(2**attempt, 10)  # Max 10 seconds
                    logger.warning(
                        f"Client error for {target_url}: {e}, waiting {wait_time}s before retry ({attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    error_msg = f"Jina Reader fetch failed: {e}"
                    logger.error(f"{error_msg} for {target_url}")
                    return RetrievalResult(
                        text=error_msg,
                        source_url=target_url,
                        retrieval_type="jina_reader",
                    )
            except Exception as e:
                error_msg = f"Jina Reader fetch failed: {e}"
                logger.error(f"{error_msg} for {target_url}")
                return RetrievalResult(
                    text=error_msg, source_url=target_url, retrieval_type="jina_reader"
                )

        # Should not reach here, but just in case
        error_msg = f"Jina Reader fetch failed after {max_retries} retries"
        return RetrievalResult(
            text=error_msg, source_url=target_url, retrieval_type="jina_reader"
        )
