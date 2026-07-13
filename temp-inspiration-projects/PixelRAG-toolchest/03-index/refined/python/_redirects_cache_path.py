def _redirects_cache_path(self) -> Path:
        return Path(str(self.zim_path) + ".redirects.json")
