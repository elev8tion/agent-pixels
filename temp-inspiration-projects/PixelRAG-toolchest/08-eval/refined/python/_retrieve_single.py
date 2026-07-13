async def _retrieve_single(self, query: str, example: dict) -> RetrievalResult:
        example_id = example.get("id", "")
        loop = asyncio.get_event_loop()

        # Priority: pixel_query_map > iNaturalist image > text-only
        pixel_query_path = None
        if self.pixel_query_map and example_id in self.pixel_query_map:
            pixel_query_path = self.pixel_query_map[example_id]

        # Check for iNaturalist query image (multimodal text+image query)
        inat_image_path = self._get_inat_image_path(example)

        try:
            # Determine query modality
            query_image = None
            if pixel_query_path and os.path.exists(pixel_query_path):
                # Pixel query: image-only (rendered text as image)
                query_image = pixel_query_path
                query_text = None
                retrieval_type = "tiled_qwen3vl_embedding_pixel_query"
            elif self.multimodal_query_text_only:
                # Ablation: text-only (no image)
                query_image = None
                query_text = query
                retrieval_type = "tiled_qwen3vl_embedding_multimodal_textonly"
            elif self.multimodal_query_image_only and inat_image_path:
                # Ablation: image-only (no text)
                query_image = inat_image_path
                query_text = None
                retrieval_type = "tiled_qwen3vl_embedding_multimodal_imageonly"
            elif inat_image_path:
                # Multimodal: text + image
                query_image = inat_image_path
                query_text = query
                retrieval_type = "tiled_qwen3vl_embedding_multimodal"
            else:
                # Text-only (no query image available)
                query_text = query
                retrieval_type = "tiled_qwen3vl_embedding"

            results = await loop.run_in_executor(
                None,
                lambda: self.retrieval_system.search(
                    text=query_text, image=query_image, top_k=self.top_k
                ),
            )

            if results:
                source_url = self._extract_urls_from_results(results)
                return RetrievalResult(
                    images=results,
                    source_url=source_url,
                    retrieval_type=retrieval_type,
                    pixel_query_path=pixel_query_path or inat_image_path,
                    query_image_path=inat_image_path,
                )
            else:
                return RetrievalResult(
                    text="No relevant tiles found via Qwen3-VL-Embedding search",
                    retrieval_type=retrieval_type,
                    pixel_query_path=pixel_query_path or inat_image_path,
                    query_image_path=inat_image_path,
                )
        except Exception as e:
            logger.error(f"Qwen3-VL-Embedding search failed: {e}")
            return RetrievalResult(
                text=f"Qwen3-VL-Embedding retrieval error: {e}",
                retrieval_type="tiled_qwen3vl_embedding",
                pixel_query_path=pixel_query_path or inat_image_path,
                query_image_path=inat_image_path,
            )
