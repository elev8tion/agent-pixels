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
