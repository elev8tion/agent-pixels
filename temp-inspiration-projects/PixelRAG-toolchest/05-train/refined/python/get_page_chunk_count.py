def get_page_chunk_count(entry: dict, tiles_root: Path) -> int:
    cached = entry.get("_chunk_count")
    if cached is not None:
        return cached

    tiles_dir = tiles_root / entry["tiles_dir"]
    chunks_json = tiles_dir / "chunks.json"
    if not chunks_json.exists():
        entry["_chunk_count"] = 0
        return 0

    with open(chunks_json) as f:
        meta = json.load(f)

    chunk_count = len(meta.get("chunks", []))
    entry["_chunk_count"] = chunk_count
    return chunk_count
