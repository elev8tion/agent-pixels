def _cache_path(self) -> Path:
        return Path(str(self.zim_path) + ".articles.json")
