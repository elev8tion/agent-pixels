def _article_dir(self, article_id: int) -> str:
        return os.path.join(self.cache_dir, f"{article_id}.png.tiles")
