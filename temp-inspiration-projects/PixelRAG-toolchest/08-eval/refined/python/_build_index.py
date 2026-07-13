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
