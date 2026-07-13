def scan_chunks(shard_dir: str) -> list[dict]:
    """Scan for chunk images in a shard directory.

    Looks for *.png.tiles/chunks.json files. Falls back to tiles.json if no chunks.
    """
    shard = Path(shard_dir)
    items = []

    for entry in sorted(shard.iterdir()):
        if not entry.is_dir():
            continue
        tile_dirs = []
        if entry.name.endswith(".png.tiles"):
            tile_dirs = [entry]
        else:
            tile_dirs = sorted(
                d
                for d in entry.iterdir()
                if d.is_dir() and d.name.endswith(".png.tiles")
            )

        for td in tile_dirs:
            dir_name = td.name
            article_id_str = dir_name.replace(".png.tiles", "")
            try:
                article_id = int(article_id_str)
            except ValueError:
                article_id = hash(article_id_str) % (2**31)

            chunks_json = td / "chunks.json"
            tiles_json = td / "tiles.json"

            if chunks_json.exists():
                with open(chunks_json) as f:
                    manifest = json.load(f)
                for chunk_info in manifest.get("chunks", []):
                    chunk_path = td / chunk_info["file"]
                    if chunk_path.exists():
                        items.append(
                            {
                                "path": str(chunk_path),
                                "article_id": article_id,
                                "tile_index": chunk_info.get("tile_index", 0),
                                "chunk_index": chunk_info.get("chunk_index", 0),
                                "y_offset": chunk_info.get("y_offset", 0),
                                "height": chunk_info.get("height", 1024),
                            }
                        )
            elif tiles_json.exists():
                with open(tiles_json) as f:
                    manifest = json.load(f)
                for i, tile_name in enumerate(manifest.get("tiles", [])):
                    tile_path = td / tile_name
                    if tile_path.exists():
                        items.append(
                            {
                                "path": str(tile_path),
                                "article_id": article_id,
                                "tile_index": i,
                                "chunk_index": 0,
                                "y_offset": 0,
                                "height": 0,
                            }
                        )

    return items
