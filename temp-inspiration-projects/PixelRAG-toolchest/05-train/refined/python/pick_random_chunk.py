def pick_random_chunk(entry: dict, tiles_root: Path) -> tuple:
    tiles_dir = tiles_root / entry["tiles_dir"]
    chunks_json = tiles_dir / "chunks.json"

    if not chunks_json.exists():
        return None, None

    with open(chunks_json) as f:
        meta = json.load(f)

    chunks = meta.get("chunks", [])
    if not chunks:
        return None, None

    usable = chunks[: max(1, int(len(chunks) * 0.7))]
    chunk = random.choice(usable)
    chunk_path = tiles_dir / chunk["file"]

    if not chunk_path.exists():
        return None, None

    return str(chunk_path), chunk["chunk_index"]
