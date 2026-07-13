def _build_article_list(self) -> list[str]:
        if self._article_paths is not None:
            return self._article_paths
        cached = self._load_article_cache()
        if cached is not None:
            self._article_paths = cached
            return self._article_paths
        zim = self._get_zim()
        logger.info("Building article list from ZIM (%d entries)...", zim.entry_count)
        paths = []
        for i in range(zim.entry_count):
            try:
                entry = zim._get_entry_by_id(i)
                path = entry.path
                if self._is_article_path(path):
                    if not entry.is_redirect:
                        paths.append(path)
            except Exception:
                continue
            if i % 1_000_000 == 0 and i > 0:
                logger.info(
                    "  Scanned %dM / %dM entries, %d articles so far",
                    i // 1_000_000,
                    zim.entry_count // 1_000_000,
                    len(paths),
                )
        self._article_paths = paths
        logger.info("Found %d articles in ZIM", len(paths))
        self._save_article_cache(paths)
        return self._article_paths
