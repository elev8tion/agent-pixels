def _load_cache(self):
        if not os.path.isfile(self.cache_path):
            return
        import json

        loaded = 0
        try:
            with open(self.cache_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    self._cache[entry["path"]] = entry["text"]
                    loaded += 1
            logger.info(
                f"OCRWrappedRetriever: loaded {loaded} cached OCR entries from {self.cache_path}"
            )
        except Exception as e:
            logger.warning(
                f"OCRWrappedRetriever: cache load failed ({e}); starting fresh"
            )
