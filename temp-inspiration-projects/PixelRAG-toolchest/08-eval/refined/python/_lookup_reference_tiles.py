def _lookup_reference_tiles(self, examples: list[dict]) -> dict[str, list[dict]]:
        """Look up reference URL tiles from kiwix for each example.

        Returns dict: example_id -> list of hit dicts with path/score/url/is_reference.
        """
        import sys as _sys
        from .simpleqa_data import extract_url_from_metadata

        if not os.path.isdir(_KIWIX_OUTPUT_DIR) or not os.path.isfile(
            _KIWIX_ARTICLES_JSON
        ):
            logger.error(
                f"lookup_reference_url: kiwix tiles unavailable at {_KIWIX_OUTPUT_DIR}"
            )
            return {}

        if _WIKI_SCREENSHOT_DIR not in _sys.path:
            _sys.path.insert(0, _WIKI_SCREENSHOT_DIR)
        from scripts.build_index import batch_query_by_url as _batch_query

        # Collect URLs, group by URL to avoid duplicate lookups
        url_to_eids: dict[str, list[str]] = {}
        for ex in examples:
            eid = ex.get("id", "unknown")
            url = extract_url_from_metadata(ex)
            if url and "wikipedia.org" in url:
                url_to_eids.setdefault(url, []).append(eid)

        if not url_to_eids:
            return {}

        redirects = (
            _KIWIX_REDIRECTS_JSON if os.path.isfile(_KIWIX_REDIRECTS_JSON) else None
        )
        results = _batch_query(
            _KIWIX_OUTPUT_DIR,
            list(url_to_eids.keys()),
            _KIWIX_ARTICLES_JSON,
            redirects_json=redirects,
        )

        ref_tiles: dict[str, list[dict]] = {}
        found, missing = 0, 0
        for url, eids in url_to_eids.items():
            result = results.get(url)
            if result is None:
                missing += 1
                logger.warning(f"lookup_reference_url: URL not found in kiwix: {url}")
                continue
            tiles_dir_abs = os.path.join(_KIWIX_OUTPUT_DIR, result["tiles_dir"])
            if not os.path.isdir(tiles_dir_abs):
                missing += 1
                logger.warning(
                    f"lookup_reference_url: tiles dir missing: {tiles_dir_abs}"
                )
                continue
            chunks = sorted(
                f
                for f in os.listdir(tiles_dir_abs)
                if f.startswith("chunk_") and f.endswith(".png")
            )
            if not chunks:
                missing += 1
                logger.warning(
                    f"lookup_reference_url: no chunk files in {tiles_dir_abs}"
                )
                continue
            found += 1
            hits = [
                {
                    "path": os.path.join(tiles_dir_abs, c),
                    "score": 0.0,
                    "url": url,
                    "is_reference": True,
                }
                for c in chunks
            ]
            for eid in eids:
                ref_tiles[eid] = hits

        logger.info(
            f"lookup_reference_url: batch lookup {found} found, {missing} missing "
            f"out of {len(url_to_eids)} unique URLs"
        )
        return ref_tiles
