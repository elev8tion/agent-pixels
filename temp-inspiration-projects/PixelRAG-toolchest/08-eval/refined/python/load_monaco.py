def load_monaco(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"MoNaCo dataset not found at {path}\n"
            f"Download from https://github.com/facebookresearch/MoNaCo\n"
            f"Place the JSONL file at: {DEFAULT_DATA_PATH}\n"
            f"Or pass --data-path <path>"
        )
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows
