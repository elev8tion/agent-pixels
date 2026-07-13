class OCRWrappedRetriever(BaseRetriever):
    """Wraps an image retriever; OCRs retrieved tiles and returns text.

    Ablation A pipeline: image retrieve -> OCR -> text to reader.
    Talks to an OpenAI-compatible chat endpoint (PaddleOCR-VL served via vLLM).
    Caches OCR output to a JSONL file keyed by absolute image path so reruns
    reuse prior work.
    """

    DEFAULT_PROMPT = "OCR this image. Output only the extracted text verbatim, preserving paragraph and line breaks."

    def __init__(
        self,
        base: BaseRetriever,
        ocr_url: str = "http://localhost:8202/v1",
        model: str = "PaddlePaddle/PaddleOCR-VL",
        api_key: str = "dummy",
        cache_path: str = "ocr_cache/paddleocr_vl.jsonl",
        concurrency: int = 16,
        prompt: str | None = None,
        timeout: float = 180.0,
        max_tokens: int = 4096,
        reader_top_k: int | None = None,
    ):
        self.base = base
        self.ocr_url = ocr_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.cache_path = cache_path
        self.concurrency = concurrency
        self.prompt = prompt or self.DEFAULT_PROMPT
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.reader_top_k = reader_top_k
        self._cache: dict[str, str] = {}
        self.tiles_dir = getattr(base, "tiles_dir", None)
        self._load_cache()

    def _load_cache(self):
        if not os.path.isfile(self.cache_path):
            return
        import json

        loaded = 0
        try:
            with open(self.cache_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    self._cache[entry["path"]] = entry["text"]
                    loaded += 1
            logger.info(
                f"OCRWrappedRetriever: loaded {loaded} cached OCR entries from {self.cache_path}"
            )
        except Exception as e:
            logger.warning(
                f"OCRWrappedRetriever: cache load failed ({e}); starting fresh"
            )

    def _append_cache(self, path: str, text: str):
        import json

        os.makedirs(os.path.dirname(self.cache_path) or ".", exist_ok=True)
        with open(self.cache_path, "a") as f:
            f.write(json.dumps({"path": path, "text": text}, ensure_ascii=False) + "\n")
        self._cache[path] = text

    async def _ocr_one(self, path: str, session) -> str:
        if path in self._cache:
            return self._cache[path]
        import aiohttp
        import base64

        try:
            with open(path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("ascii")
        except Exception as e:
            logger.error(f"OCR read failed for {path}: {e}")
            return ""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                        },
                        {"type": "text", "text": self.prompt},
                    ],
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": 0.0,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with session.post(
                f"{self.ocr_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                if resp.status != 200:
                    err = await resp.text()
                    logger.error(f"OCR HTTP {resp.status} for {path}: {err[:200]}")
                    return ""
                result = await resp.json()
                text = result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OCR request failed for {path}: {e}")
            return ""
        self._append_cache(path, text)
        return text

    async def _batch_ocr(self, paths: list[str]) -> dict[str, str]:
        import aiohttp

        to_fetch = [p for p in paths if p not in self._cache]
        if not to_fetch:
            return {p: self._cache[p] for p in paths}
        sem = asyncio.Semaphore(self.concurrency)
        async with aiohttp.ClientSession() as session:

            async def _one(p):
                async with sem:
                    return await self._ocr_one(p, session)

            await asyncio.gather(*[_one(p) for p in to_fetch])
        return {p: self._cache.get(p, "") for p in paths}

    async def prefetch(self, examples: list[dict]):
        """Forward to base's prefetch, then batch-OCR all tiles up front."""
        if hasattr(self.base, "prefetch"):
            await self.base.prefetch(examples)
        all_paths: set[str] = set()
        for ex in examples:
            r = await self.base.retrieve(ex.get("problem", ""), ex)
            images = (
                r.images[: self.reader_top_k]
                if self.reader_top_k is not None
                else r.images
            )
            for p, _ in images:
                all_paths.add(os.path.abspath(p))
        uncached = [p for p in all_paths if p not in self._cache]
        logger.info(
            f"OCRWrappedRetriever: {len(all_paths)} unique tiles across {len(examples)} examples; "
            f"{len(all_paths) - len(uncached)} cached, OCRing {len(uncached)}"
        )
        if uncached:
            await self._batch_ocr(uncached)

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        r = await self.base.retrieve(query, example)
        if not r.images:
            return r
        images = (
            r.images[: self.reader_top_k] if self.reader_top_k is not None else r.images
        )
        image_urls = (
            r.image_urls[: self.reader_top_k]
            if self.reader_top_k is not None and r.image_urls
            else list(r.image_urls or [])
        )
        urls: list[str] = []
        seen_urls: set[str] = set()
        for url in image_urls:
            if url and url not in seen_urls:
                seen_urls.add(url)
                urls.append(url)
        paths = [os.path.abspath(p) for p, _ in images]
        ocr_map = await self._batch_ocr(paths)
        passages = [ocr_map[p].strip() for p in paths if ocr_map.get(p, "").strip()]
        combined = "\n\n---\n\n".join(passages) if passages else None
        return RetrievalResult(
            text=combined,
            images=[],
            source_url=", ".join(urls) if urls else r.source_url,
            retrieval_type=f"{r.retrieval_type}+ocr",
            pixel_query_path=r.pixel_query_path,
            query_image_path=r.query_image_path,
        )
