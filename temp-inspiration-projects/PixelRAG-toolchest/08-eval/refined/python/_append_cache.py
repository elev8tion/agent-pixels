def _append_cache(self, path: str, text: str):
        import json

        os.makedirs(os.path.dirname(self.cache_path) or ".", exist_ok=True)
        with open(self.cache_path, "a") as f:
            f.write(json.dumps({"path": path, "text": text}, ensure_ascii=False) + "\n")
        self._cache[path] = text
