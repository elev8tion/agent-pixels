def _delete_tiles_in_shard(shard_dir: str) -> int:
    """Delete tile_*.png for all articles with chunks.json in a shard.

    Tiles referenced directly as chunk files (h <= 1024) are preserved.
    """
    deleted = 0
    for sub in Path(shard_dir).iterdir():
        if not sub.is_dir() or not sub.name.startswith("shard_"):
            continue
        for article_dir in sub.iterdir():
            if not article_dir.is_dir() or not article_dir.name.endswith(".png.tiles"):
                continue
            cj_path = article_dir / "chunks.json"
            if not cj_path.exists():
                continue
            # Collect tile files referenced as chunks (small tiles, not split)
            try:
                with open(cj_path) as f:
                    manifest = json.load(f)
                keep = {
                    c["file"]
                    for c in manifest.get("chunks", [])
                    if c["file"].startswith("tile_")
                }
            except (json.JSONDecodeError, KeyError):
                keep = set()
            for f in article_dir.iterdir():
                if f.name.startswith("tile_") and f.name.endswith(
                    (".png", ".jpg", ".jpeg")
                ):
                    if f.name not in keep:
                        f.unlink()
                        deleted += 1
    return deleted
