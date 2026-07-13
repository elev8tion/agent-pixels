def find_chunk_paths(tiles_dir: Path, article_id: int) -> list[str]:
    """Find all chunk PNG paths for a given article ID."""
    shard_size = 8284
    top_shard = article_id // shard_size
    top_dir = tiles_dir / f"shard_{top_shard:03d}"
    if not top_dir.exists():
        return []
    tile_dir_name = f"{article_id}.png.tiles"
    # Search sub-shards
    for sub in top_dir.iterdir():
        if not sub.is_dir() or not sub.name.startswith("shard_"):
            continue
        candidate = sub / tile_dir_name
        if candidate.exists():
            chunks_json = candidate / "chunks.json"
            if chunks_json.exists():
                try:
                    chunks = json.loads(chunks_json.read_text())
                    return [
                        str(candidate / c["file"])
                        for c in chunks.get("chunks", [])
                        if (candidate / c["file"]).exists()
                    ]
                except (json.JSONDecodeError, KeyError):
                    pass
    return []
