class TextVectorRetriever(BaseRetriever):
    """Retrieve text using LEANN vector search.

    Uses LEANN's integrated embedding + indexing system for text retrieval.
    Supports various embedding models (Qwen3, nomic-embed-text, OpenAI, etc.)
    """

    def __init__(
        self,
        text_cache: dict,
        index_path: str,
        embedding_model: str = "Qwen/Qwen3-Embedding-0.6B",
        embedding_mode: str = "sentence-transformers",
        embedding_options: dict | None = None,
        top_k: int = 3,
        rebuild_index: bool = False,
        chunk_size: int = 512,
        chunk_overlap: int = 128,
    ):
        """Initialize TextVectorRetriever.

        Args:
            text_cache: Dict of {id: {"text": ..., "url": ...}}
            index_path: Path to LEANN index
            embedding_model: Embedding model name (default: Qwen/Qwen3-Embedding-0.6B)
            embedding_mode: Embedding mode (sentence-transformers, openai, gemini, ollama)
            embedding_options: Additional options for embedding (e.g., base_url, api_key for OpenAI-compatible APIs)
            top_k: Number of results to retrieve
            rebuild_index: Force rebuild index even if exists
            chunk_size: Max tokens per chunk (default: 512)
            chunk_overlap: Overlap tokens between chunks (default: 128)
        """
        import sys
        from pathlib import Path as PathLib

        # Add LEANN to path
        leann_path = (
            PathLib(__file__).parent.parent.parent
            / "LEANN"
            / "packages"
            / "leann-core"
            / "src"
        )
        if str(leann_path) not in sys.path:
            sys.path.insert(0, str(leann_path))

        from leann.api import LeannBuilder, LeannSearcher

        self.text_cache = text_cache
        self.top_k = top_k
        self.index_path = index_path
        self.embedding_model = embedding_model
        self.embedding_mode = embedding_mode
        self.embedding_options = embedding_options or {}
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Check if index exists
        meta_path = f"{index_path}.meta.json"
        index_exists = os.path.exists(meta_path)

        if rebuild_index or not index_exists:
            logger.info(f"Building LEANN text index at {index_path}...")
            self._build_index(LeannBuilder)
            logger.info(f"LEANN text index built with {len(text_cache)} documents")
        else:
            logger.info(f"Loading existing LEANN text index from {index_path}")

        # Load searcher
        self.searcher = LeannSearcher(index_path)
        logger.info(
            f"TextVectorRetriever ready with {len(text_cache)} documents, top_k={top_k}"
        )

    def _build_index(self, LeannBuilder):
        """Build LEANN index from text_cache with chunking for long texts."""
        builder = LeannBuilder(
            backend_name="hnsw",
            embedding_model=self.embedding_model,
            embedding_mode=self.embedding_mode,
            embedding_options=self.embedding_options,
            is_recompute=False,  # Store embeddings to avoid recomputing at search time
        )

        # Chunking parameters (from CLI or defaults)
        max_tokens = self.chunk_size
        overlap_tokens = self.chunk_overlap

        # Import tiktoken for accurate chunking
        try:
            import tiktoken

            enc = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            enc = None
            logger.warning("tiktoken not available, using character-based chunking")

        chunk_count = 0
        for example_id, data in self.text_cache.items():
            text = data.get("text", "")
            url = data.get("url", "")
            if not text:
                continue

            if enc:
                # Token-based chunking
                tokens = enc.encode(text)
                if len(tokens) <= max_tokens:
                    # Short text, add as single passage
                    builder.add_text(text, metadata={"id": example_id, "url": url})
                    chunk_count += 1
                else:
                    # Long text, chunk it with overlap
                    start = 0
                    chunk_idx = 0
                    while start < len(tokens):
                        end = min(start + max_tokens, len(tokens))
                        chunk_tokens = tokens[start:end]
                        chunk_text = enc.decode(chunk_tokens)

                        chunk_id = f"{example_id}_chunk_{chunk_idx}"
                        builder.add_text(
                            chunk_text,
                            metadata={
                                "id": chunk_id,
                                "original_id": example_id,
                                "url": url,
                                "chunk_idx": chunk_idx,
                            },
                        )
                        chunk_count += 1
                        chunk_idx += 1

                        if end >= len(tokens):
                            break
                        start = end - overlap_tokens  # Overlap
            else:
                # Fallback: character-based chunking (~4 chars per token)
                max_chars = max_tokens * 4
                overlap_chars = overlap_tokens * 4

                if len(text) <= max_chars:
                    builder.add_text(text, metadata={"id": example_id, "url": url})
                    chunk_count += 1
                else:
                    start = 0
                    chunk_idx = 0
                    while start < len(text):
                        end = min(start + max_chars, len(text))
                        chunk_text = text[start:end]

                        chunk_id = f"{example_id}_chunk_{chunk_idx}"
                        builder.add_text(
                            chunk_text,
                            metadata={
                                "id": chunk_id,
                                "original_id": example_id,
                                "url": url,
                                "chunk_idx": chunk_idx,
                            },
                        )
                        chunk_count += 1
                        chunk_idx += 1

                        if end >= len(text):
                            break
                        start = end - overlap_chars

        logger.info(
            f"Created {chunk_count} chunks from {len(self.text_cache)} documents"
        )

        # Build index
        builder.build_index(self.index_path)

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        """Retrieve relevant texts using LEANN vector search."""
        del example  # Not used - retrieval is from pre-built index
        loop = asyncio.get_event_loop()

        try:
            # Run search in executor (LEANN search is sync)
            results = await loop.run_in_executor(
                None,
                lambda: self.searcher.search(
                    query, top_k=self.top_k, recompute_embeddings=False
                ),
            )

            if results:
                # Combine retrieved texts
                texts = []
                urls = []
                for r in results:
                    texts.append(r.text)
                    url = r.metadata.get("url", "") if r.metadata else ""
                    urls.append(url)

                combined_text = "\n\n---\n\n".join(texts)
                combined_urls = ", ".join(u for u in urls if u)

                return RetrievalResult(
                    text=combined_text,
                    source_url=combined_urls,
                    retrieval_type="text_vector",
                )
        except Exception as e:
            logger.warning(f"Text vector retrieval failed: {e}")

        return RetrievalResult(retrieval_type="text_vector")
