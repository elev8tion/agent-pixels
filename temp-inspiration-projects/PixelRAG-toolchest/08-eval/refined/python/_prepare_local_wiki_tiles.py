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
