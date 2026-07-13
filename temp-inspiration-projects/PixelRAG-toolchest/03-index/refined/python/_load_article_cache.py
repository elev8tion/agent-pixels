def _load_article_cache(self) -> Optional[list[str]]:
        cache = self._cache_path()
        if not cache.exists():
            return None
        try:
            with open(cache, "r") as f:
                paths = json.load(f)
            logger.info("Loaded %d articles from cache %s", len(paths), cache)
            return paths
        except Exception as e:
            logger.warning("Failed to load article cache: %s", e)
            return None
