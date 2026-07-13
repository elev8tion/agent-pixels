def _resolve_path(article_id: int, tile_index: int, chunk_index: int) -> str:
    """Resolve chunk file path from article_id, tile_index, chunk_index."""
    tiles_dir = _state["tiles_dir"]
    shard_size = _state.get("shard_size", 8284)
    tiles_dirname = f"{article_id}.png.tiles"
    chunk_name = f"chunk_{tile_index:04d}_{chunk_index:02d}.png"

    # Flat layout: tiles_dir/{article_id}.png.tiles/chunk_XXXX_YY.png
    flat_path = os.path.join(tiles_dir, tiles_dirname, chunk_name)
    if os.path.exists(flat_path):
        return flat_path

    # Sharded layout: tiles_dir/shard_XXX/sub/{article_id}.png.tiles/chunk_XXXX_YY.png
    top_shard = article_id // shard_size
    top_shard_dir = os.path.join(tiles_dir, f"shard_{top_shard:03d}")
    if os.path.isdir(top_shard_dir):
        for sub in sorted(os.listdir(top_shard_dir)):
            sub_path = os.path.join(top_shard_dir, sub, tiles_dirname)
            if os.path.isdir(sub_path):
                return os.path.join(sub_path, chunk_name)

    # Fallback: shard path without checking existence (serve may run without tiles)
    top_shard = article_id // shard_size
    return os.path.join(
        tiles_dir, f"shard_{top_shard:03d}", "?", tiles_dirname, chunk_name
    )
