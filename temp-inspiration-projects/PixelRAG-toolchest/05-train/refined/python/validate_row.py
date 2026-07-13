def validate_row(args):
    """Validate a single JSONL row. Returns (line, is_valid)."""
    line, jsonl_dir = args
    item = json.loads(line)

    # Resolve positive path
    path = Path(item["chunk_path"])
    if not path.is_absolute():
        path = (jsonl_dir / path).resolve()
    pos_path = str(path)

    if not os.path.exists(pos_path):
        return line, False, "missing"
    try:
        with Image.open(pos_path) as im:
            im.convert("RGB").verify()
    except Exception:
        return line, False, "corrupt"

    # Check neg paths exist (no image verify — too slow and rarely corrupt)
    if "neg_chunk_paths" in item:
        valid_negs = []
        for np_ in item["neg_chunk_paths"]:
            np_path = Path(np_)
            if not np_path.is_absolute():
                np_path = (jsonl_dir / np_path).resolve()
            if os.path.exists(str(np_path)):
                valid_negs.append(np_)
        item["neg_chunk_paths"] = valid_negs
        return json.dumps(item, ensure_ascii=False) + "\n", True, "ok"

    return line, True, "ok"
