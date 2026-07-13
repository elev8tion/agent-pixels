def resolve_jsonl_path(jsonl_path, path_str):
    """Resolve a possibly relative path against a JSONL file location."""
    path = Path(path_str)
    if path.is_absolute():
        return str(path.resolve())
    return str((Path(jsonl_path).resolve().parent / path).resolve())
