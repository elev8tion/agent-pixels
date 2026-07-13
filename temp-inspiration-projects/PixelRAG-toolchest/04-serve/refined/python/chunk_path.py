def chunk_path(
        self, article_id: int, title: str, tile_index: int, chunk_index: int
    ):
        """Path to chunk_{ti}_{ci}.png, rendering+chunking the page on a cache miss."""
        chunk_name = f"chunk_{tile_index:04d}_{chunk_index:02d}.png"
        cpath = os.path.join(self._article_dir(article_id), chunk_name)
        if os.path.exists(cpath):
            return cpath
        if not title:
            return None
        with _render_lock:
            if os.path.exists(cpath):  # filled while we waited for the lock
                return cpath
            try:
                self._render_and_chunk(article_id, title)
            except Exception:
                return None
        return cpath if os.path.exists(cpath) else None
