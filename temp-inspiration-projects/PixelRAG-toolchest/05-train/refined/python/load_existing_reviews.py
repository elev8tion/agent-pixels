def load_existing_reviews(path: Path) -> dict[int, dict]:
    existing = {}
    if not path.exists():
        return existing
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            existing[int(item["row_id"])] = item
    return existing
