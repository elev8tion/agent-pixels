async def retrieve_multi_image(self, query: str, example: dict) -> RetrievalResult:
        """Multi-image retrieval: search with ALL query images, aggregate scores, return top-K.

        For each query image, does a multimodal search (text + image), then combines
        scores across all images using max-score aggregation per tile.
        Falls back to single-image retrieve() if only 0-1 images available.
        """
        all_image_paths = _get_all_query_image_paths(example, self.tiles_dir)
        # Get single image for generation (first available, used in RetrievalResult)
        single_image_path = self._get_inat_image_path(example)

        if len(all_image_paths) <= 1:
            return await self._retrieve_single(query, example)

        example_id = example.get("id", "")
        loop = asyncio.get_event_loop()
        logger.info(
            f"Multi-image retrieval for {example_id}: {len(all_image_paths)} query images"
        )

        try:
            # Score aggregation: for each tile, keep the max score across all query images
            tile_best_score: dict[str, float] = {}

            for img_path in all_image_paths:
                results = await loop.run_in_executor(
                    None,
                    lambda p=img_path: self.retrieval_system.search(
                        text=query, image=p, top_k=self.top_k * 2
                    ),
                )
                for tile_path, score in results:
                    if (
                        tile_path not in tile_best_score
                        or score > tile_best_score[tile_path]
                    ):
                        tile_best_score[tile_path] = score

            # Sort by score descending, take top_k
            sorted_tiles = sorted(
                tile_best_score.items(), key=lambda x: x[1], reverse=True
            )
            top_results = sorted_tiles[: self.top_k]

            retrieval_type = (
                f"tiled_qwen3vl_embedding_multiimage_{len(all_image_paths)}imgs"
            )

            if top_results:
                source_url = self._extract_urls_from_results(top_results)
                return RetrievalResult(
                    images=top_results,
                    source_url=source_url,
                    retrieval_type=retrieval_type,
                    pixel_query_path=single_image_path,
                    query_image_path=single_image_path,
                )
            else:
                return RetrievalResult(
                    text="No relevant tiles found via multi-image search",
                    retrieval_type=retrieval_type,
                    pixel_query_path=single_image_path,
                    query_image_path=single_image_path,
                )
        except Exception as e:
            logger.error(f"Multi-image retrieval failed: {e}")
            return await self._retrieve_single(query, example)
