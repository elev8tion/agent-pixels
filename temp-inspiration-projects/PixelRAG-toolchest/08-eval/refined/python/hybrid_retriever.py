class HybridRetriever(BaseRetriever):
    """Merge image (LocalAPIRetriever) and text (TextAPIRetriever) hits by raw score.

    Both underlying retrievers embed with Qwen3-VL-Embedding-2B against L2-normalized
    FAISS IVFFlat (IP metric) indices, so their per-hit scores are cosine similarities
    on the same scale and directly comparable without any normalization step.

    Each base is called with its own configured top_k, then the combined candidate pool
    is sorted by score desc and the top `top_k` are kept. The reader receives the
    surviving image hits as image inputs and the surviving text hits as a concatenated
    text block in the same prompt — VL-4B handles mixed modality natively.
    """

    def __init__(
        self,
        image_base: "LocalAPIRetriever",
        text_base: "TextAPIRetriever",
        top_k: int = 3,
        reader_top_k: int | None = None,
    ):
        if not hasattr(image_base, "get_hits"):
            raise TypeError(
                f"HybridRetriever.image_base requires get_hits(); got {type(image_base).__name__}"
            )
        if not hasattr(text_base, "get_hits"):
            raise TypeError(
                f"HybridRetriever.text_base requires get_hits(); got {type(text_base).__name__}"
            )
        self.image_base = image_base
        self.text_base = text_base
        self.top_k = top_k
        self.reader_top_k = reader_top_k
        self.tiles_dir = getattr(image_base, "tiles_dir", None)

    async def prefetch(self, examples: list[dict]):
        if hasattr(self.image_base, "prefetch"):
            await self.image_base.prefetch(examples)
        if hasattr(self.text_base, "prefetch"):
            await self.text_base.prefetch(examples)

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        image_hits = await self.image_base.get_hits(query, example)
        text_hits = await self.text_base.get_hits(query, example)

        # Tag each hit with its modality, then merge and sort by score desc.
        merged: list[tuple[float, str, dict]] = []
        for h in image_hits:
            score = float(h.get("score", 0.0))
            merged.append((score, "image", h))
        for h in text_hits:
            score = float(h.get("score", 0.0))
            merged.append((score, "text", h))

        merged.sort(key=lambda x: x[0], reverse=True)
        keep_k = self.reader_top_k if self.reader_top_k is not None else self.top_k
        top = merged[:keep_k]

        images: list[tuple[str, float]] = []
        passages: list[str] = []
        urls: list[str] = []
        seen_urls: set[str] = set()

        for score, modality, hit in top:
            url = hit.get("url", "")
            if modality == "image":
                path = hit.get("path", "")
                if path and os.path.exists(path):
                    images.append((path, score))
            else:  # text
                title = hit.get("title", "")
                text = hit.get("text", "")
                if text:
                    header = f"[{title}]" if title else ""
                    passages.append(f"{header}\n{text}" if header else text)
            if url and url not in seen_urls:
                seen_urls.add(url)
                urls.append(url)

        return RetrievalResult(
            text="\n\n".join(passages) if passages else None,
            images=images,
            source_url=", ".join(urls) if urls else None,
            retrieval_type="hybrid",
        )
