class LocalAPIRetriever(BaseRetriever):
    """Retrieve tiles from a local search API (e.g. localhost:30888/search).

    The API accepts batch queries:
        {"queries": [{"text": "..."}, ...], "n_docs": N}
    and returns:
        {"results": [{"hits": [{"path": ..., "url": ..., "score": ...}, ...]}, ...]}

    Call prefetch(examples) before the main loop to batch all queries in one API
    call. Individual retrieve() calls then return cached results instantly.

    When query_rewrite is enabled, uses an LLM to rewrite questions into
    keyword-rich search queries before retrieval.
    """

    REWRITE_PROMPT = (
        "You are a search query optimizer. Given a trivia/factual question, "
        "rewrite it as a Wikipedia search query that would find the article "
        "containing the answer. Output ONLY the search query, nothing else.\n\n"
        "Rules:\n"
        "- Focus on the key entity or topic the question is about\n"
        "- Include all specific names, dates, awards, events, or other details mentioned\n"
        "- Remove filler words like 'what is', 'who was', 'in which year'\n"
        "- Preserve all proper nouns and technical terms exactly as written\n\n"
        "Question: {question}\n"
        "Search query:"
    )

    def __init__(
        self,
        api_url: str = "http://localhost:30888/search",
        top_k: int = 5,
        batch_size: int = 32,
        query_rewrite: bool = False,
        rewrite_model: str | None = None,
        rewrite_api_base: str | None = None,
        rewrite_api_key: str = "dummy",
        nprobe: int | None = None,
        reranker=None,
        rerank_top_k: int = 3,
        query_image_fn=None,
        multi_image_query: bool = False,
        tiles_dir: str = "tiles/evqa",
        lookup_reference_url: bool = False,
        query_instruction: str | None = None,
    ):
        self.api_url = api_url
        self.top_k = top_k
        self.batch_size = batch_size
        self.query_rewrite = query_rewrite
        self.rewrite_model = rewrite_model
        self.rewrite_api_base = rewrite_api_base
        self.rewrite_api_key = rewrite_api_key
        self.nprobe = nprobe
        self.reranker = reranker
        self.rerank_top_k = rerank_top_k
        self.query_image_fn = query_image_fn  # callable(example) -> image_path or None
        self.multi_image_query = multi_image_query
        self.tiles_dir = tiles_dir
        self.lookup_reference_url = lookup_reference_url
        self.query_instruction = query_instruction
        self._cache: dict[str, list[dict]] = {}  # example_id -> hits
        self._rewritten_queries: dict[str, str] = {}  # example_id -> rewritten query

    async def _rewrite_queries(self, examples: list[dict]) -> dict[str, str]:
        """Batch-rewrite questions into search queries using an LLM."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=self.rewrite_api_key,
            base_url=self.rewrite_api_base,
            timeout=60.0,
        )

        rewritten = {}
        sem = asyncio.Semaphore(20)

        async def rewrite_one(ex):
            eid = ex.get("id", "unknown")
            prompt = self.REWRITE_PROMPT.format(question=ex["problem"])
            async with sem:
                try:
                    resp = await client.chat.completions.create(
                        model=self.rewrite_model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
                        max_tokens=200,
                    )
                    rewritten[eid] = resp.choices[0].message.content.strip()
                except Exception as e:
                    logger.warning(f"Query rewrite failed for {eid}: {e}")
                    rewritten[eid] = ex["problem"]  # fallback to original

        await asyncio.gather(*[rewrite_one(ex) for ex in examples])
        return rewritten

    def _lookup_reference_tiles(self, examples: list[dict]) -> dict[str, list[dict]]:
        """Look up reference URL tiles from kiwix for each example.

        Returns dict: example_id -> list of hit dicts with path/score/url/is_reference.
        """
        import sys as _sys
        from .simpleqa_data import extract_url_from_metadata

        if not os.path.isdir(_KIWIX_OUTPUT_DIR) or not os.path.isfile(
            _KIWIX_ARTICLES_JSON
        ):
            logger.error(
                f"lookup_reference_url: kiwix tiles unavailable at {_KIWIX_OUTPUT_DIR}"
            )
            return {}

        if _WIKI_SCREENSHOT_DIR not in _sys.path:
            _sys.path.insert(0, _WIKI_SCREENSHOT_DIR)
        from scripts.build_index import batch_query_by_url as _batch_query

        # Collect URLs, group by URL to avoid duplicate lookups
        url_to_eids: dict[str, list[str]] = {}
        for ex in examples:
            eid = ex.get("id", "unknown")
            url = extract_url_from_metadata(ex)
            if url and "wikipedia.org" in url:
                url_to_eids.setdefault(url, []).append(eid)

        if not url_to_eids:
            return {}

        redirects = (
            _KIWIX_REDIRECTS_JSON if os.path.isfile(_KIWIX_REDIRECTS_JSON) else None
        )
        results = _batch_query(
            _KIWIX_OUTPUT_DIR,
            list(url_to_eids.keys()),
            _KIWIX_ARTICLES_JSON,
            redirects_json=redirects,
        )

        ref_tiles: dict[str, list[dict]] = {}
        found, missing = 0, 0
        for url, eids in url_to_eids.items():
            result = results.get(url)
            if result is None:
                missing += 1
                logger.warning(f"lookup_reference_url: URL not found in kiwix: {url}")
                continue
            tiles_dir_abs = os.path.join(_KIWIX_OUTPUT_DIR, result["tiles_dir"])
            if not os.path.isdir(tiles_dir_abs):
                missing += 1
                logger.warning(
                    f"lookup_reference_url: tiles dir missing: {tiles_dir_abs}"
                )
                continue
            chunks = sorted(
                f
                for f in os.listdir(tiles_dir_abs)
                if f.startswith("chunk_") and f.endswith(".png")
            )
            if not chunks:
                missing += 1
                logger.warning(
                    f"lookup_reference_url: no chunk files in {tiles_dir_abs}"
                )
                continue
            found += 1
            hits = [
                {
                    "path": os.path.join(tiles_dir_abs, c),
                    "score": 0.0,
                    "url": url,
                    "is_reference": True,
                }
                for c in chunks
            ]
            for eid in eids:
                ref_tiles[eid] = hits

        logger.info(
            f"lookup_reference_url: batch lookup {found} found, {missing} missing "
            f"out of {len(url_to_eids)} unique URLs"
        )
        return ref_tiles

    async def prefetch(self, examples: list[dict]):
        """Batch-fetch retrieval results for all examples via the API."""
        import aiohttp

        # Step 1: Query rewriting (if enabled)
        if self.query_rewrite and self.rewrite_model:
            to_rewrite = [
                ex
                for ex in examples
                if ex.get("id", "unknown") not in self._rewritten_queries
            ]
            if to_rewrite:
                logger.info(
                    f"LocalAPIRetriever: rewriting {len(to_rewrite)} queries..."
                )
                self._rewritten_queries.update(await self._rewrite_queries(to_rewrite))
                # Log some examples
                for ex in to_rewrite[:3]:
                    eid = ex.get("id", "unknown")
                    orig = ex["problem"][:60]
                    rewr = self._rewritten_queries.get(eid, "")[:60]
                    logger.info(f"  Rewrite: '{orig}...' -> '{rewr}'")

        # Step 2: Build query list
        queries = []
        example_ids = []

        if self.multi_image_query:
            # Multi-image: send one query per image, track which example each belongs to
            # We'll aggregate after receiving results
            multi_image_groups: dict[
                str, list[int]
            ] = {}  # eid -> list of indices in queries[]
            for ex in examples:
                eid = ex.get("id", "unknown")
                if eid in self._cache:
                    continue
                if self.query_rewrite and eid in self._rewritten_queries:
                    query_text = self._rewritten_queries[eid]
                else:
                    query_text = ex["problem"]

                all_paths = _get_all_query_image_paths(ex, self.tiles_dir)
                if len(all_paths) <= 1:
                    # Single or no image: just use the standard path
                    query_dict = {"text": query_text}
                    if all_paths:
                        import base64

                        with open(all_paths[0], "rb") as f:
                            query_dict["image"] = base64.b64encode(f.read()).decode()
                    elif self.query_image_fn:
                        img_path = self.query_image_fn(ex)
                        if img_path and os.path.exists(img_path):
                            import base64

                            with open(img_path, "rb") as f:
                                query_dict["image"] = base64.b64encode(
                                    f.read()
                                ).decode()
                    multi_image_groups[eid] = [len(queries)]
                    queries.append(query_dict)
                    example_ids.append(eid)
                else:
                    # Multiple images: one query per image
                    group_indices = []
                    import base64

                    for img_path in all_paths:
                        query_dict = {"text": query_text}
                        with open(img_path, "rb") as f:
                            query_dict["image"] = base64.b64encode(f.read()).decode()
                        group_indices.append(len(queries))
                        queries.append(query_dict)
                        example_ids.append(eid)
                    multi_image_groups[eid] = group_indices
                    logger.info(
                        f"Multi-image query for {eid[:8]}: {len(all_paths)} images"
                    )
        else:
            for ex in examples:
                eid = ex.get("id", "unknown")
                if eid in self._cache:
                    continue
                if self.query_rewrite and eid in self._rewritten_queries:
                    query_text = self._rewritten_queries[eid]
                else:
                    query_text = ex["problem"]
                query_dict = {"text": query_text}
                if self.query_image_fn:
                    img_path = self.query_image_fn(ex)
                    if img_path and os.path.exists(img_path):
                        import base64

                        with open(img_path, "rb") as f:
                            query_dict["image"] = base64.b64encode(f.read()).decode()
                queries.append(query_dict)
                example_ids.append(eid)

        if not queries:
            logger.info("LocalAPIRetriever: all examples already cached")
            return

        # Use smaller batches when queries contain images (GPU memory)
        has_images = any("image" in q for q in queries)
        batch_size = min(self.batch_size, 16) if has_images else self.batch_size
        logger.info(
            f"LocalAPIRetriever: prefetching {len(queries)} queries in batches of {batch_size}"
            f"{' (multimodal)' if has_images else ''}"
        )

        for batch_start in range(0, len(queries), batch_size):
            batch_queries = queries[batch_start : batch_start + batch_size]
            batch_ids = example_ids[batch_start : batch_start + batch_size]

            n_docs = self.top_k * 2 if self.multi_image_query else self.top_k
            payload = {
                "queries": batch_queries,
                "n_docs": n_docs,
                "include_images": True,
            }
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
                                f"Local API batch error {response.status}: {error_text[:200]}"
                            )
                            for eid in batch_ids:
                                self._cache[eid] = []
                            continue
                        result = await response.json()
            except Exception as e:
                logger.error(f"Local API batch call failed: {e}")
                for eid in batch_ids:
                    self._cache[eid] = []
                continue

            results_list = result.get("results", [])
            for i, eid in enumerate(batch_ids):
                if i < len(results_list):
                    hits = results_list[i].get("hits", [])
                else:
                    hits = []
                if eid not in self._cache:
                    self._cache[eid] = hits
                else:
                    # Multi-image: accumulate hits from all images for this example
                    self._cache[eid].extend(hits)

            logger.info(
                f"  Batch {batch_start // batch_size + 1}/{(len(queries) + batch_size - 1) // batch_size}: "
                f"{len(batch_queries)} queries done"
            )

        # Multi-image aggregation: deduplicate and keep max score per tile path
        if self.multi_image_query:
            for eid in list(self._cache.keys()):
                hits = self._cache[eid]
                if not hits:
                    continue
                # Aggregate by path: keep hit with max score
                best_by_path: dict[str, dict] = {}
                for hit in hits:
                    path = hit.get("path", "")
                    score = hit.get("score", 0.0)
                    if path not in best_by_path or score > best_by_path[path].get(
                        "score", 0.0
                    ):
                        best_by_path[path] = hit
                # Sort by score descending, take top_k
                sorted_hits = sorted(
                    best_by_path.values(),
                    key=lambda h: h.get("score", 0.0),
                    reverse=True,
                )
                self._cache[eid] = sorted_hits[: self.top_k]

        logger.info(f"LocalAPIRetriever: prefetch complete, {len(self._cache)} cached")

        # Step 2.5: Merge reference URL tiles (if enabled) — chunk-level dedup
        if self.lookup_reference_url:
            ref_tiles = self._lookup_reference_tiles(examples)
            total_added, total_skipped = 0, 0
            for eid, ref_hits in ref_tiles.items():
                existing = self._cache.get(eid, [])
                existing_paths = {hit.get("path", "") for hit in existing}
                new_chunks = [rh for rh in ref_hits if rh["path"] not in existing_paths]
                skipped = len(ref_hits) - len(new_chunks)
                if new_chunks:
                    logger.info(
                        f"  [{eid[:8]}]: adding {len(new_chunks)} reference URL chunks "
                        f"({skipped} already in API results)"
                    )
                    self._cache[eid] = existing + new_chunks
                    total_added += len(new_chunks)
                total_skipped += skipped
            logger.info(
                f"lookup_reference_url: added {total_added} chunks, "
                f"skipped {total_skipped} duplicates"
            )

        # Step 3: Rerank (if reranker provided)
        if self.reranker is not None:
            # Build batch of (query, candidates) for all examples
            batch_inputs = []
            batch_eids = []
            for ex in examples:
                eid = ex.get("id", "unknown")
                hits = self._cache.get(eid, [])
                if not hits:
                    continue
                candidates = []
                for hit in hits:
                    path = hit.get("path", "")
                    score = hit.get("score", 0.0)
                    if path and os.path.exists(path):
                        candidates.append((path, score))
                if not candidates:
                    continue
                batch_inputs.append((ex["problem"], candidates))
                batch_eids.append(eid)

            if batch_inputs:
                all_reranked = self.reranker.rerank_batch(
                    batch_inputs,
                    top_k=self.rerank_top_k,
                )
                # Update cache with reranked results
                for eid, reranked_results in zip(batch_eids, all_reranked):
                    hits = self._cache[eid]
                    path_to_hit = {hit["path"]: hit for hit in hits if "path" in hit}
                    new_hits = []
                    for path, rerank_score in reranked_results:
                        orig_hit = path_to_hit.get(path, {})
                        new_hits.append(
                            {**orig_hit, "path": path, "score": rerank_score}
                        )
                    self._cache[eid] = new_hits
                logger.info(
                    f"LocalAPIRetriever: reranking complete ({len(batch_inputs)} examples)"
                )

    @staticmethod
    @staticmethod
    def _resolve_tile_path(hit: dict, tiles_dir: str | None = None) -> str | None:
        """Resolve tile path from hit, searching local shard dirs if needed."""
        path = hit.get("path", "")
        if path and os.path.exists(path):
            return path
        if not tiles_dir:
            return path if path else None
        article_id = hit.get("article_id")
        tile_index = hit.get("tile_index", 0)
        chunk_index = hit.get("chunk_index", 0)
        if article_id is None:
            return path if path else None
        tiles_dirname = f"{article_id}.png.tiles"
        chunk_name = f"chunk_{tile_index:04d}_{chunk_index:02d}.png"
        shard_size = 8284
        top_shard = article_id // shard_size
        top_shard_dir = os.path.join(tiles_dir, f"shard_{top_shard:03d}")
        if os.path.isdir(top_shard_dir):
            for sub in sorted(os.listdir(top_shard_dir)):
                sub_path = os.path.join(top_shard_dir, sub, tiles_dirname)
                if os.path.isdir(sub_path):
                    full = os.path.join(sub_path, chunk_name)
                    if os.path.exists(full):
                        return full
        flat = os.path.join(tiles_dir, tiles_dirname, chunk_name)
        if os.path.exists(flat):
            return flat
        return path if path else None

    @staticmethod
    def _hits_to_result(
        hits: list[dict], tiles_dir: str | None = None
    ) -> RetrievalResult:
        """Convert API hits to RetrievalResult."""
        if not hits:
            return RetrievalResult(retrieval_type="local_api")

        images = []
        image_urls = []
        urls = []
        seen_urls = set()
        for hit in hits:
            score = hit.get("score", 0.0)
            url = hit.get("url", "")
            path = LocalAPIRetriever._resolve_tile_path(hit, tiles_dir)
            if path and os.path.exists(path):
                images.append((path, score))
                image_urls.append(url or None)
            elif hit.get("image_base64"):
                images.append((hit["image_base64"], score))
                image_urls.append(url or None)
            if url and url not in seen_urls:
                seen_urls.add(url)
                urls.append(url)

        return RetrievalResult(
            images=images,
            image_urls=image_urls,
            source_url=", ".join(urls) if urls else None,
            retrieval_type="local_api",
        )

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        eid = example.get("id", "unknown")

        # Return cached result if available (from prefetch)
        if eid in self._cache:
            return self._hits_to_result(self._cache[eid], tiles_dir=self.tiles_dir)

        # Fallback: single query (if prefetch wasn't called)
        import aiohttp

        query_dict = {"text": query}
        if self.query_image_fn:
            img_path = self.query_image_fn(example)
            if img_path and os.path.exists(img_path):
                import base64

                with open(img_path, "rb") as f:
                    query_dict["image"] = base64.b64encode(f.read()).decode()
        payload = {"queries": [query_dict], "n_docs": self.top_k}
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
                        return RetrievalResult(retrieval_type="local_api")
                    result = await response.json()
        except Exception as e:
            logger.error(f"Local API call failed: {e}")
            return RetrievalResult(retrieval_type="local_api")

        hits = result.get("results", [{}])[0].get("hits", [])
        self._cache[eid] = hits
        return self._hits_to_result(hits, tiles_dir=self.tiles_dir)

    async def get_hits(self, query: str, example: dict) -> list[dict]:
        """Return raw per-hit dicts (path/url/score/...) for this example.

        Used by wrappers that need per-hit granularity (e.g. HybridRetriever).
        Uses the same cache as retrieve().
        """
        await self.retrieve(query, example)
        return self._cache.get(example.get("id", "unknown"), [])
