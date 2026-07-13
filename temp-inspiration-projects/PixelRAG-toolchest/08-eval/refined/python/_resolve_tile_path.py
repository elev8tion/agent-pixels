@staticmethod
    @staticmethod
    def _resolve_tile_path(hit: dict, tiles_dir: str | None = None) -> str | None:
        """Resolve tile path from hit, searching local shard dirs if needed."""
        path = hit.get("path", "")
        if path and os.path.exists(path):
            return path
        if not tiles_dir:
            return path if path else None
        article_id = hit.get("article_id")
        tile_index = hit.get("tile_index", 0)
        chunk_index = hit.get("chunk_index", 0)
        if article_id is None:
            return path if path else None
        tiles_dirname = f"{article_id}.png.tiles"
        chunk_name = f"chunk_{tile_index:04d}_{chunk_index:02d}.png"
        shard_size = 8284
        top_shard = article_id // shard_size
        top_shard_dir = os.path.join(tiles_dir, f"shard_{top_shard:03d}")
        if os.path.isdir(top_shard_dir):
            for sub in sorted(os.listdir(top_shard_dir)):
                sub_path = os.path.join(top_shard_dir, sub, tiles_dirname)
                if os.path.isdir(sub_path):
                    full = os.path.join(sub_path, chunk_name)
                    if os.path.exists(full):
                        return full
        flat = os.path.join(tiles_dir, tiles_dirname, chunk_name)
        if os.path.exists(flat):
            return flat
        return path if path else None
