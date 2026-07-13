def process_shard(
    shard_dir: str,
    dry_run: bool = False,
    force: bool = False,
    delete_tiles: bool = False,
) -> dict:
    """Chunk all articles in a shard directory."""
    t0 = time.time()
    total_articles = 0
    chunked_articles = 0
    skipped_articles = 0
    total_tiles = 0
    total_chunks = 0
    total_files = 0

    # Walk sub-shard directories (shard_00000, shard_00001, ...)
    sub_dirs = sorted(
        p
        for p in Path(shard_dir).iterdir()
        if p.is_dir() and p.name.startswith("shard_")
    )

    if not sub_dirs:
        # Flat structure — article dirs directly in shard_dir
        sub_dirs = [Path(shard_dir)]

    for sub_dir in sub_dirs:
        for article_dir in sorted(sub_dir.iterdir()):
            if not article_dir.is_dir() or not article_dir.name.endswith(".png.tiles"):
                continue
            total_articles += 1

            result = chunk_article(str(article_dir), dry_run=dry_run, force=force)
            if result is None:
                skipped_articles += 1
                continue

            chunked_articles += 1
            total_tiles += result["num_tiles"]
            total_chunks += result["num_chunks"]
            total_files += result["files_written"]

    # Delete tiles after chunking the whole shard
    tiles_deleted = 0
    if delete_tiles and not dry_run:
        tiles_deleted = _delete_tiles_in_shard(shard_dir)

    elapsed = time.time() - t0
    shard_name = os.path.basename(shard_dir.rstrip("/"))
    return {
        "shard": shard_name,
        "articles": total_articles,
        "chunked": chunked_articles,
        "skipped": skipped_articles,
        "tiles": total_tiles,
        "chunks": total_chunks,
        "files_written": total_files,
        "tiles_deleted": tiles_deleted,
        "elapsed_s": round(elapsed, 1),
    }
