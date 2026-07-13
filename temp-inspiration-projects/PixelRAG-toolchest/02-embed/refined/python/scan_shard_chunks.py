def scan_shard_chunks(
    shard_dir: str,
    skip_article_ids: set[int] | None = None,
) -> list[ChunkInfo]:
    """Walk a shard directory and collect all chunk images.

    Looks for ``*.png.tiles/chunks.json`` files. Each entry in
    ``meta["chunks"]`` becomes one ChunkInfo.

    Args:
        shard_dir: Path to a shard directory.
        skip_article_ids: Article IDs to skip (already embedded).

    Returns:
        Sorted list of ChunkInfo (by article_id, tile_index, chunk_index).
    """
    shard_path = Path(shard_dir)
    skip = skip_article_ids or set()
    chunks: list[ChunkInfo] = []

    tile_dirs: list[Path] = []
    for entry in sorted(shard_path.iterdir()):
        if entry.is_dir() and entry.name.startswith("shard_"):
            for sub_entry in sorted(entry.iterdir()):
                if sub_entry.is_dir() and sub_entry.name.endswith(".png.tiles"):
                    tile_dirs.append(sub_entry)
        elif entry.is_dir() and entry.name.endswith(".png.tiles"):
            tile_dirs.append(entry)

    for tiles_dir in tile_dirs:
        chunks_json = tiles_dir / "chunks.json"
        if not chunks_json.exists():
            continue

        try:
            meta = json.loads(chunks_json.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Skipping %s: %s", chunks_json, e)
            continue

        dir_name = tiles_dir.name
        try:
            article_id = int(dir_name.split(".")[0])
        except (ValueError, IndexError):
            logger.warning("Cannot parse article_id from %s", dir_name)
            continue

        if article_id in skip:
            continue

        page_height = meta.get("page_height", 0)
        viewport_width = meta.get("viewport_width", 875)

        for chunk in meta.get("chunks", []):
            chunk_path = tiles_dir / chunk["file"]
            if chunk_path.exists():
                chunks.append(
                    ChunkInfo(
                        article_id=article_id,
                        tile_index=chunk["tile_index"],
                        chunk_index=chunk["chunk_index"],
                        chunk_path=str(chunk_path),
                        page_height=page_height,
                        viewport_width=viewport_width,
                        y_offset=chunk["y_offset"],
                        chunk_height=chunk["height"],
                    )
                )

    chunks.sort(key=lambda c: (c.article_id, c.tile_index, c.chunk_index))
    logger.info(
        "Scanned %s: %d chunks from %d articles",
        shard_dir,
        len(chunks),
        len({c.article_id for c in chunks}),
    )
    return chunks
