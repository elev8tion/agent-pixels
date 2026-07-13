def iter_jsonl(path: Path, offset: int, limit: int):
    yielded = 0
    with path.open(encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx < offset:
                continue
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)
            yielded += 1
            if limit > 0 and yielded >= limit:
                break
