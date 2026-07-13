class TiledQwen3VLEmbeddingRetriever(BaseRetriever):
    """Retrieves context by searching through image tiles using Qwen3-VL-Embedding.

    Uses single vector embeddings (2048 dim) with cosine similarity for retrieval.

    When *pixel_query_map* is provided the retriever embeds the rendered query
    image (pixel query) instead of the raw text, so retrieval happens entirely
    in pixel space.
    """

    def __init__(
        self,
        screenshot_dir: str = "screenshots",
        tiles_dir: str = "tiles",
        tile_size: int | tuple[int, int] = 512,
        overlap: int = 0,
        cache_path: str | None = None,
        model_name: str = "Qwen/Qwen3-VL-Embedding-2B",
        top_k: int = 3,
        examples: list[dict] | None = None,
        gpu_ids: list[int] | None = None,
        tensor_parallel_size: int = 1,
        pixel_query_map: dict[str, str] | None = None,
        multimodal_query_text_only: bool = False,
        multimodal_query_image_only: bool = False,
        local_wiki: bool = False,
        local_wiki_screenshot_dir: str | None = None,
        multi_image_query: bool = False,
        prebuilt_tiles_dir: str | None = None,
        embedding_backend: str = "vllm",  # "vllm", "hf", or "biqwen3"
        peft_adapter: str | None = None,
    ):
        self.top_k = top_k
        self.screenshot_dir = screenshot_dir
        self.tiles_dir = tiles_dir
        self.tile_size = tile_size
        self.overlap = overlap
        self.examples = examples or []
        self.pixel_query_map = pixel_query_map  # example_id -> pixel query image path
        self.multimodal_query_text_only = multimodal_query_text_only
        self.multimodal_query_image_only = multimodal_query_image_only
        self.local_wiki = local_wiki
        self.local_wiki_screenshot_dir = local_wiki_screenshot_dir
        self.multi_image_query = multi_image_query
        self.prebuilt_tiles_dir = prebuilt_tiles_dir
        self.embedding_backend = embedding_backend
        self.peft_adapter = peft_adapter
        os.makedirs(screenshot_dir, exist_ok=True)
        os.makedirs(tiles_dir, exist_ok=True)

        # Build example_id -> URL mapping and deduplicate by URL
        from .simpleqa_data import extract_url_from_metadata

        self.id_to_url = {}
        seen_urls: dict[str, str] = {}  # url -> first example_id that uses it
        self.url_to_representative_id: dict[
            str, str
        ] = {}  # url -> representative example_id
        dedup_examples = []
        for ex in self.examples:
            ex_id = ex.get("id", "")
            url = extract_url_from_metadata(ex)
            if url:
                self.id_to_url[ex_id] = url
                if url not in seen_urls:
                    seen_urls[url] = ex_id
                    self.url_to_representative_id[url] = ex_id
                    dedup_examples.append(ex)

        logger.info(
            f"Deduplicated {len(self.examples)} examples -> {len(dedup_examples)} unique URLs "
            f"(removed {len(self.examples) - len(dedup_examples)} duplicate pages)"
        )
        self._dedup_examples = dedup_examples

        # Prepare tile paths: prebuilt dir (hard mini-datastore), local-wiki, or Selenium
        if self.prebuilt_tiles_dir:
            tile_paths = self._load_prebuilt_tiles()
        elif self.local_wiki:
            tile_paths = self._prepare_local_wiki_tiles()
        else:
            tile_paths = self._prepare_screenshots_and_tiles()

        # Import Qwen3-VL-Embedding retrieval system
        import sys
        from pathlib import Path

        scripts_dir = Path(__file__).parent.parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        try:
            from qwen3vl_embedding_retrieval import Qwen3VLEmbeddingSystem
        except ImportError:
            try:
                from scripts.qwen3vl_embedding_retrieval import Qwen3VLEmbeddingSystem
            except ImportError:
                raise ImportError("Qwen3VLEmbeddingSystem not available.")

        logger.info("Initializing Qwen3-VL-Embedding retrieval system...")
        logger.info(f"Model: {model_name}, tiles: {len(tile_paths)}, GPUs: {gpu_ids}")
        if self.pixel_query_map:
            logger.info(
                f"Pixel query mode ENABLED ({len(self.pixel_query_map)} queries)"
            )

        self.retrieval_system = Qwen3VLEmbeddingSystem(
            model_name=model_name,
            cache_path=cache_path,
            gpu_ids=gpu_ids,
            tensor_parallel_size=tensor_parallel_size,
            backend=self.embedding_backend,
            peft_adapter=self.peft_adapter,
        )

        # Embed all tiles (batch_size=8 for HF backend to avoid OOM on shared GPUs)
        embed_bs = 8 if self.embedding_backend == "hf" else 32
        self.retrieval_system.embed_images(
            file_paths=tile_paths,
            cache_path=cache_path,
            batch_size=embed_bs,
        )
        logger.info(
            f"Qwen3-VL-Embedding retrieval ready with {len(self.retrieval_system.image_paths)} tiles"
        )

    def _load_prebuilt_tiles(self) -> list[str]:
        """Load ALL .png tiles from a prebuilt tile directory (e.g. hard mini-datastore).

        Unlike _prepare_local_wiki_tiles which only loads golden tiles matching
        example IDs, this loads every tile in the directory — including distractors.
        """
        import glob as _glob

        all_tiles = sorted(_glob.glob(os.path.join(self.prebuilt_tiles_dir, "*.png")))
        filtered = _filter_tiles_by_aspect_ratio(all_tiles)
        logger.info(
            f"prebuilt-tiles: loaded {len(filtered)} tiles from {self.prebuilt_tiles_dir} "
            f"(filtered {len(all_tiles) - len(filtered)} extreme aspect ratio tiles)"
        )
        return filtered

    def _prepare_local_wiki_tiles(self) -> list[str]:
        """Prepare tiles from local kiwix tile store for all examples in the batch.

        Does a single batch URL lookup (fast), then copies+cuts tiles per example.
        Reports an error (no fallback) if a URL is not found in kiwix.

        Returns the list of all cut tile paths ready for embedding.
        """
        import glob as _glob
        import shutil
        import sys as _sys
        from PIL import Image
        from .simpleqa_data import extract_url_from_metadata
        from tqdm import tqdm

        cut_height = (
            self.tile_size[1] if isinstance(self.tile_size, tuple) else self.tile_size
        )
        wiki_cache = self.local_wiki_screenshot_dir or os.path.join(
            self.screenshot_dir, "local-wiki"
        )
        os.makedirs(wiki_cache, exist_ok=True)
        os.makedirs(self.tiles_dir, exist_ok=True)

        # Separate already-cached examples from ones that need processing
        need: list[tuple[str, str]] = []  # (ex_id, url)
        for ex in self._dedup_examples:
            ex_id = ex["id"]
            if not _glob.glob(os.path.join(self.tiles_dir, f"{ex_id}_tile_*.png")):
                url = extract_url_from_metadata(ex) or ""
                need.append((ex_id, url))

        logger.info(
            f"local-wiki: {len(self._dedup_examples) - len(need)} cached, {len(need)} need processing"
        )

        if need:
            # Single batch lookup for all URLs at once (loads articles.json once)
            if not os.path.isdir(_KIWIX_OUTPUT_DIR) or not os.path.isfile(
                _KIWIX_ARTICLES_JSON
            ):
                logger.error(
                    f"local-wiki: kiwix tiles unavailable at {_KIWIX_OUTPUT_DIR}"
                )
            else:
                if _WIKI_SCREENSHOT_DIR not in _sys.path:
                    _sys.path.insert(0, _WIKI_SCREENSHOT_DIR)
                from scripts.build_index import batch_query_by_url as _batch_query

                redirects = (
                    _KIWIX_REDIRECTS_JSON
                    if os.path.isfile(_KIWIX_REDIRECTS_JSON)
                    else None
                )
                urls_to_lookup = [u for _, u in need if u and "wikipedia.org" in u]
                results = _batch_query(
                    _KIWIX_OUTPUT_DIR,
                    urls_to_lookup,
                    _KIWIX_ARTICLES_JSON,
                    redirects_json=redirects,
                )
                found = sum(1 for r in results.values() if r is not None)
                logger.info(
                    f"local-wiki: batch lookup found {found}/{len(urls_to_lookup)} URLs"
                )

                # Copy + cut per example
                ok, failed = 0, 0
                for ex_id, url in tqdm(need, desc="local-wiki: copying+cutting tiles"):
                    # Check cache again (may have been done by a parallel run)
                    if _glob.glob(os.path.join(self.tiles_dir, f"{ex_id}_tile_*.png")):
                        ok += 1
                        continue
                    result = results.get(url)
                    if result is None:
                        logger.error(
                            f"local-wiki [{ex_id}]: URL not found in kiwix: {url}"
                        )
                        failed += 1
                        continue
                    src_dir = os.path.join(_KIWIX_OUTPUT_DIR, result["tiles_dir"])
                    article_cache = os.path.join(wiki_cache, str(ex_id))
                    if not os.path.exists(article_cache):
                        if not os.path.isdir(src_dir):
                            logger.error(
                                f"local-wiki [{ex_id}]: tiles dir not on disk: {src_dir}"
                            )
                            failed += 1
                            continue
                        shutil.copytree(src_dir, article_cache)
                    # Cut into strips
                    raw_tiles = sorted(
                        f
                        for f in os.listdir(article_cache)
                        if f.endswith(".png") and f.startswith("tile_")
                    )
                    if not raw_tiles:
                        logger.error(
                            f"local-wiki [{ex_id}]: no tile PNGs in {article_cache}"
                        )
                        failed += 1
                        continue
                    global_row = 0
                    for raw_name in raw_tiles:
                        raw_path = os.path.join(article_cache, raw_name)
                        if os.path.getsize(raw_path) == 0:
                            continue
                        try:
                            img = Image.open(raw_path)
                            img.load()
                        except Exception as e:
                            logger.warning(
                                f"local-wiki [{ex_id}]: corrupt tile {raw_path}: {e}"
                            )
                            continue
                        w, h = img.size
                        y = 0
                        while y < h:
                            y2 = min(y + cut_height, h)
                            img.crop((0, y, w, y2)).save(
                                os.path.join(
                                    self.tiles_dir, f"{ex_id}_tile_{global_row}_0.png"
                                )
                            )
                            global_row += 1
                            y += cut_height
                        img.close()
                    ok += 1
                logger.info(
                    f"local-wiki: {ok} articles prepared, {failed} not found/failed"
                )

        all_tile_paths = []
        for ex in self._dedup_examples:
            ex_id = ex["id"]
            tiles = sorted(
                _glob.glob(os.path.join(self.tiles_dir, f"{ex_id}_tile_*.png"))
            )
            all_tile_paths.extend(tiles)

        filtered = _filter_tiles_by_aspect_ratio(all_tile_paths)
        logger.info(
            f"local-wiki: {len(filtered)} tiles ready for embedding "
            f"(filtered {len(all_tile_paths) - len(filtered)} extreme aspect ratio tiles)"
        )
        return filtered

    def _prepare_screenshots_and_tiles(self) -> list[str]:
        """Prepare screenshots and tiles for dataset, return tile paths.

        Uses deduplicated examples (one per unique URL) to avoid
        duplicate tiles inflating the retrieval index.
        """
        from .simpleqa_data import capture_screenshot_for_example, split_image_to_tiles
        from tqdm import tqdm

        examples_to_process = self._dedup_examples
        screenshot_paths = []
        missing = []

        # Collect screenshot paths and identify missing (deduplicated)
        for ex in examples_to_process:
            screenshot_path = os.path.join(
                self.screenshot_dir, f"{ex['id']}_fullhd.png"
            )
            screenshot_paths.append(screenshot_path)
            if (
                not os.path.exists(screenshot_path)
                or os.path.getsize(screenshot_path) == 0
            ):
                missing.append(ex)

        # Capture missing screenshots
        if missing:
            logger.info(f"Preparing {len(missing)} missing screenshots...")
            for ex in tqdm(missing, desc="Capturing screenshots"):
                capture_screenshot_for_example(ex, self.screenshot_dir)
            logger.info("Screenshots prepared.")

        # Split each screenshot into tiles
        all_tile_paths = []
        logger.info(
            f"Splitting {len(screenshot_paths)} unique screenshots into tiles (output: {self.tiles_dir})..."
        )
        for screenshot_path in tqdm(screenshot_paths, desc="Splitting tiles"):
            if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
                tile_paths = split_image_to_tiles(
                    screenshot_path, self.tiles_dir, self.tile_size, self.overlap
                )
                all_tile_paths.extend(tile_paths)

        # Filter out tiles with extreme aspect ratios
        filtered_tile_paths = _filter_tiles_by_aspect_ratio(all_tile_paths)
        logger.info(
            f"Prepared {len(filtered_tile_paths)} tiles from {len(screenshot_paths)} unique screenshots "
            f"(filtered {len(all_tile_paths) - len(filtered_tile_paths)} extreme aspect ratio tiles)"
        )
        return filtered_tile_paths

    def _extract_urls_from_results(self, results: list) -> str:
        """Extract source URLs from tile paths in results, preserving retrieval order."""
        urls = []
        seen = set()
        for item in results:
            # item is (path, score) tuple
            path = item[0] if isinstance(item, tuple) else item
            # Extract example_id from tile path: {example_id}_fullhd_tile_{x}_{y}.png
            filename = os.path.basename(path)
            if "_tile_" in filename:
                example_id = filename.split("_tile_")[0]
                if example_id.endswith("_fullhd"):
                    example_id = example_id[:-7]
                if example_id in self.id_to_url:
                    url = self.id_to_url[example_id]
                    if url not in seen:
                        seen.add(url)
                        urls.append(url)
        return ", ".join(urls)

    # Class-level cache for iNat 2021 image_id -> file_name mapping
    _inat2021_id_map: dict[int, str] | None = None
    INAT2021_DATA_DIR = _INAT2021_DATA_DIR

    @classmethod
    def _load_inat2021_mapping(cls) -> dict[int, str]:
        """Load iNaturalist 2021 competition image_id -> file_name mapping.

        Downloads val.json from the competition S3 bucket if not cached locally.
        """
        if cls._inat2021_id_map is not None:
            return cls._inat2021_id_map

        import json
        import tarfile
        import urllib.request
        from pathlib import Path

        data_dir = Path(cls.INAT2021_DATA_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)
        val_json = data_dir / "val.json"

        if not val_json.exists():
            tar_path = data_dir / "val.json.tar.gz"
            if not tar_path.exists():
                logger.info("Downloading iNaturalist 2021 val annotations...")
                urllib.request.urlretrieve(
                    "https://ml-inat-competition-datasets.s3.amazonaws.com/2021/val.json.tar.gz",
                    str(tar_path),
                )
            with tarfile.open(str(tar_path), "r:gz") as tf:
                tf.extractall(path=str(data_dir))
            logger.info(f"Extracted iNat 2021 val.json to {val_json}")

        with open(val_json) as f:
            data = json.load(f)

        cls._inat2021_id_map = {img["id"]: img["file_name"] for img in data["images"]}
        logger.info(f"Loaded iNat 2021 mapping: {len(cls._inat2021_id_map)} images")
        return cls._inat2021_id_map

    def _get_inat_image_path(self, example: dict) -> str | None:
        """Get EVQA query image (iNaturalist or Landmarks). Delegates to _get_query_image_path_for_example."""
        return _get_query_image_path_for_example(example, self.tiles_dir)

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        # Dispatch to multi-image retrieval if enabled
        if self.multi_image_query:
            return await self.retrieve_multi_image(query, example)
        return await self._retrieve_single(query, example)

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
