class RenderedTextWrapper(BaseRetriever):
    """Wraps a text retriever; renders each chunk as an image.

    Ablation B pipeline: text retrieve -> render as Wikipedia-style image -> VLM reader.
    Requires the base retriever to expose get_hits(query, example) returning
    per-hit dicts with keys: title, text, url, score, article_id, chunk_index.
    (TextAPIRetriever satisfies this.)

    Renders are cached on disk at {render_dir}/{article_id}_{chunk_index}.png
    so repeated eval runs don't re-render.
    """

    def __init__(
        self,
        base: BaseRetriever,
        render_dir: str = "rendered_chunks",
        reader_top_k: int | None = None,
    ):
        if not hasattr(base, "get_hits"):
            raise TypeError(
                f"RenderedTextWrapper requires base retriever with get_hits(); "
                f"got {type(base).__name__}"
            )
        self.base = base
        self.render_dir = render_dir
        self.reader_top_k = reader_top_k
        os.makedirs(self.render_dir, exist_ok=True)
        self.tiles_dir = render_dir

    async def prefetch(self, examples: list[dict]):
        if hasattr(self.base, "prefetch"):
            await self.base.prefetch(examples)

    def _render(self, hit: dict) -> str:
        from .text_renderer import render_text_chunk

        article_id = hit.get("article_id", "unknown")
        chunk_index = hit.get("chunk_index", 0)
        out_path = os.path.join(self.render_dir, f"{article_id}_{chunk_index}.png")
        if os.path.isfile(out_path):
            return out_path
        # No-title policy: mirrors `_hits_to_result` (line ~3035) — title/url are
        # leaked metadata for entity-answering tasks and were stripped from the
        # text→text path on 2026-04-29. Apply the same constraint here so
        # rendered and text→text differ only in modality, not in content.
        render_text_chunk(
            text=hit.get("text", ""),
            title=None,
            url=None,
            output_path=out_path,
        )
        return out_path

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        hits = await self.base.get_hits(query, example)
        if not hits:
            return RetrievalResult(retrieval_type="text_api+rendered")
        if self.reader_top_k is not None:
            hits = hits[: self.reader_top_k]
        images: list[tuple[str, float]] = []
        urls: list[str] = []
        seen_urls: set[str] = set()
        for hit in hits:
            if not hit.get("text"):
                continue
            path = self._render(hit)
            images.append((path, float(hit.get("score", 0.0))))
            url = hit.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                urls.append(url)
        return RetrievalResult(
            images=images,
            source_url=", ".join(urls) if urls else None,
            retrieval_type="text_api+rendered",
        )
