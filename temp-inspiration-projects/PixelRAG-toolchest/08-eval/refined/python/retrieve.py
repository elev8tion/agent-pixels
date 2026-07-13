async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        """Retrieve text chunks, then do DOM lookup for HTML context."""
        example.get("id", "unknown")

        # Get raw hits from text retriever
        hits = await self._text_retriever.get_hits(query, example)
        if not hits:
            return RetrievalResult(retrieval_type="html_dom_lookup")

        keep_k = self.reader_top_k if self.reader_top_k is not None else self.top_k
        hits = hits[:keep_k]

        passages = []
        urls = []
        seen_urls: set[str] = set()

        for hit in hits:
            article_id = hit.get("article_id")
            chunk_text = hit.get("text", "")
            url = hit.get("url", "")

            html_context = None
            if article_id is not None:
                raw_html = self._fetch_html(int(article_id))
                if raw_html:
                    # Heuristic DOM lookup first
                    html_context = self._dom_lookup(raw_html, chunk_text)

                    # LLM verification/fallback
                    if self.llm_verify and (
                        html_context is None or len(chunk_text) > 500
                    ):
                        llm_result = await self._llm_dom_closure(raw_html, chunk_text)
                        if llm_result:
                            html_context = llm_result

            if html_context:
                passages.append(html_context)
            else:
                passages.append(chunk_text)

            if url and url not in seen_urls:
                seen_urls.add(url)
                urls.append(url)

        # Hard cap per passage. HTML is ~2 chars/token; reader has 65K tokens
        # with ~2K for output + system prompt. Budget ~50K tokens for context
        # = ~100K chars across all passages. Per-passage cap avoids one huge
        # article starving the others.
        MAX_PER_PASSAGE = 30000
        passages = [p[:MAX_PER_PASSAGE] for p in passages]
        MAX_TOTAL_CHARS = 90000
        total = sum(len(p) for p in passages)
        if total > MAX_TOTAL_CHARS:
            per_passage = MAX_TOTAL_CHARS // max(len(passages), 1)
            passages = [p[:per_passage] for p in passages]
            logger.warning(
                "Truncated %d passages from %d to %d total chars",
                len(passages),
                total,
                sum(len(p) for p in passages),
            )

        combined = "\n\n---\n\n".join(passages) if passages else None
        return RetrievalResult(
            text=combined,
            source_url=", ".join(urls) if urls else None,
            retrieval_type="html_dom_lookup",
        )
