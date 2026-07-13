class TextAPIRetriever(BaseRetriever):
    """Retrieve text chunks from a text search API (wiki-screenshot text_search_api.py).

    The API accepts:
        POST /search
        {"queries": [{"text": "..."}], "n_docs": N}
    and returns:
        {"results": [{"hits": [{"text": ..., "title": ..., "url": ..., "score": ...}, ...]}]}

    Supports batch prefetch for efficient evaluation.
    """

    def __init__(
        self,
        api_url: str = "http://localhost:30889/search",
        top_k: int = 3,
        batch_size: int = 32,
        nprobe: int | None = None,
        query_instruction: str | None = None,
        reader_top_k: int | None = None,
        query_image_fn=None,
    ):
        self.api_url = api_url
        self.top_k = top_k
        # If reader_top_k is set and < top_k, only the first reader_top_k hits are
        # passed to the reader. Mirrors the image-side reader_top_k slicing in
        # run_naive_simpleqa.py so text + image cells are comparable at fixed k.
        self.reader_top_k = reader_top_k
        self.batch_size = batch_size
        self.nprobe = nprobe
        self.query_instruction = query_instruction
        self.query_image_fn = query_image_fn
        self._cache: dict[str, list[dict]] = {}

    async def prefetch(self, examples: list[dict]):
        """Batch-fetch retrieval results for all examples."""
        import aiohttp

        queries = []
        example_ids = []
        for ex in examples:
            eid = ex.get("id", "unknown")
            if eid in self._cache:
                continue
            query_dict = {"text": ex["problem"]}
            if self.query_image_fn:
                img_path = self.query_image_fn(ex)
                if img_path and os.path.exists(img_path):
                    import base64

                    with open(img_path, "rb") as f:
                        query_dict["image"] = base64.b64encode(f.read()).decode()
            queries.append(query_dict)
            example_ids.append(eid)

        if not queries:
            logger.info("TextAPIRetriever: all examples already cached")
            return

        has_images = any("image" in q for q in queries)
        batch_size = min(self.batch_size, 16) if has_images else self.batch_size
        logger.info(
            f"TextAPIRetriever: prefetching {len(queries)} queries in batches of {batch_size}"
            f"{' (multimodal)' if has_images else ''}"
        )

        for batch_start in range(0, len(queries), batch_size):
            batch_queries = queries[batch_start : batch_start + batch_size]
            batch_ids = example_ids[batch_start : batch_start + batch_size]

            payload = {"queries": batch_queries, "n_docs": self.top_k}
            if self.nprobe is not None:
                payload["nprobe"] = self.nprobe
            if self.query_instruction is not None:
                payload["instruction"] = self.query_instruction
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.api_url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=600),
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(
                                f"TextAPI batch error {response.status}: {error_text[:200]}"
                            )
                            for eid in batch_ids:
                                self._cache[eid] = []
                            continue
                        result = await response.json()
            except Exception as e:
                logger.error(f"TextAPI batch call failed: {e}")
                for eid in batch_ids:
                    self._cache[eid] = []
                continue

            results_list = result.get("results", [])
            for i, eid in enumerate(batch_ids):
                if i < len(results_list):
                    self._cache[eid] = results_list[i].get("hits", [])
                else:
                    self._cache[eid] = []

            logger.info(
                f"  Batch {batch_start // self.batch_size + 1}/"
                f"{(len(queries) + self.batch_size - 1) // self.batch_size}: "
                f"{len(batch_queries)} queries done"
            )

        logger.info(f"TextAPIRetriever: prefetch complete, {len(self._cache)} cached")

    @staticmethod
    def _hits_to_result(
        hits: list[dict], max_passages: int | None = None
    ) -> RetrievalResult:
        """Convert text API hits to RetrievalResult.

        If max_passages is set, only the first max_passages hits are joined into
        the reader prompt. The cache itself is not truncated, so the same cached
        hits can serve multiple reader_top_k values.
        """
        if not hits:
            return RetrievalResult(retrieval_type="text_api")

        if max_passages is not None and max_passages < len(hits):
            hits = hits[:max_passages]

        passages = []
        urls = []
        seen_urls = set()
        for hit in hits:
            text = hit.get("text", "")
            url = hit.get("url", "")
            # Option 1 (2026-04-29): no `[title]` prefix on chunks. Title is leaked
            # metadata for entity-answering tasks (often contains the answer outright).
            # Reader sees only the chunk content. URL lives in retrieval_result.source_url
            # for logging/grading but is not injected into the prompt by build_messages.
            if text:
                passages.append(text)
            if url and url not in seen_urls:
                seen_urls.add(url)
                urls.append(url)

        combined_text = "\n\n".join(passages) if passages else None
        return RetrievalResult(
            text=combined_text,
            source_url=", ".join(urls) if urls else None,
            retrieval_type="text_api",
        )

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        eid = example.get("id", "unknown")

        if eid in self._cache:
            return self._hits_to_result(
                self._cache[eid], max_passages=self.reader_top_k
            )

        # Fallback: single query
        import aiohttp

        payload = {"queries": [{"text": query}], "n_docs": self.top_k}
        if self.nprobe is not None:
            payload["nprobe"] = self.nprobe
        if self.query_instruction is not None:
            payload["instruction"] = self.query_instruction
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300),
                ) as response:
                    if response.status != 200:
                        return RetrievalResult(retrieval_type="text_api")
                    result = await response.json()
        except Exception as e:
            logger.error(f"TextAPI call failed: {e}")
            return RetrievalResult(retrieval_type="text_api")

        hits = result.get("results", [{}])[0].get("hits", [])
        self._cache[eid] = hits
        return self._hits_to_result(hits, max_passages=self.reader_top_k)

    async def get_hits(self, query: str, example: dict) -> list[dict]:
        """Return raw per-hit dicts (title/text/url/score/...) for this example.

        Used by wrappers that need per-chunk granularity (e.g. RenderedTextWrapper).
        Uses the same cache as retrieve().
        """
        await self.retrieve(query, example)
        return self._cache.get(example.get("id", "unknown"), [])
