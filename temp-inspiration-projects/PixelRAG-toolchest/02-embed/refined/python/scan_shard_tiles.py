def scan_shard_tiles(
    shard_dir: str,
    skip_article_ids: set[int] | None = None,
) -> list[TileInfo]:
    """Walk a shard directory and collect all completed tiles.

    Looks for ``*.png.tiles/tiles.json`` files with ``complete: true``.
    Each tile PNG listed in tiles.json becomes one TileInfo entry.

    Args:
        shard_dir: Path to a shard directory (e.g. output_coordinated/shard_042).
        skip_article_ids: Article IDs to skip (already embedded).

    Returns:
        Sorted list of TileInfo (by article_id, then tile_index).
    """
    shard_path = Path(shard_dir)
    skip = skip_article_ids or set()
    tiles: list[TileInfo] = []

    # Shard directories contain sub-shard dirs (shard_00000, shard_00001, ...)
    # which contain article tile dirs (NNN.png.tiles/)
    tile_dirs: list[Path] = []
    for entry in sorted(shard_path.iterdir()):
        if entry.is_dir() and entry.name.startswith("shard_"):
            # Sub-shard directory
            for sub_entry in sorted(entry.iterdir()):
                if sub_entry.is_dir() and sub_entry.name.endswith(".png.tiles"):
                    tile_dirs.append(sub_entry)
        elif entry.is_dir() and entry.name.endswith(".png.tiles"):
            # Direct tile dir (flat shard layout)
            tile_dirs.append(entry)

    for tiles_dir in tile_dirs:
        tiles_json = tiles_dir / "tiles.json"
        if not tiles_json.exists():
            continue

        try:
            meta = json.loads(tiles_json.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Skipping %s: %s", tiles_json, e)
            continue

        if not meta.get("complete", False):
            continue

        # Extract article_id from directory name: "3104240.png.tiles" -> 3104240
        dir_name = tiles_dir.name  # e.g. "3104240.png.tiles"
        try:
            article_id = int(dir_name.split(".")[0])
        except (ValueError, IndexError):
            logger.warning("Cannot parse article_id from %s", dir_name)
            continue

        if article_id in skip:
            continue

        page_height = meta.get("page_height", 0)
        viewport_width = meta.get("viewport_width", 875)
        tile_height = meta.get("tile_height", 8192)

        for idx, tile_name in enumerate(meta.get("tiles", [])):
            tile_path = tiles_dir / tile_name
            if tile_path.exists():
                tiles.append(
                    TileInfo(
                        article_id=article_id,
                        tile_index=idx,
                        tile_path=str(tile_path),
                        page_height=page_height,
                        viewport_width=viewport_width,
                        tile_height=tile_height,
                    )
                )

    tiles.sort(key=lambda t: (t.article_id, t.tile_index))
    logger.info(
        "Scanned %s: %d tiles from %d articles",
        shard_dir,
        len(tiles),
        len({t.article_id for t in tiles}),
    )
    return tiles
