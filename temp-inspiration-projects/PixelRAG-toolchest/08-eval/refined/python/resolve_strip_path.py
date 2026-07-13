def resolve_strip_path(
    hex_id: str, strip_file: str, tiles_dir: str = NEWS_TILES_DIR
) -> str | None:
    """Resolve a pixel tile to an absolute path on disk."""
    tile_dir = Path(tiles_dir) / f"{hex_id}.tiles"
    path = tile_dir / strip_file
    return str(path) if path.exists() else None
