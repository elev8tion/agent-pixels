def _save_article_cache(self, paths: list[str]) -> None:
        cache = self._cache_path()
        tmp = cache.with_suffix(".tmp")
        try:
            with open(tmp, "w") as f:
                json.dump(paths, f)
            os.replace(tmp, cache)
            logger.info("Saved article cache (%d paths) to %s", len(paths), cache)
        except Exception as e:
            logger.warning("Failed to save article cache: %s", e)
