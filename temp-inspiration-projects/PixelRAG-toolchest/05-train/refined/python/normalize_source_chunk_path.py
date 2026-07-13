def normalize_source_chunk_path(chunk_path: str, image_root: Path) -> str:
    path = Path(chunk_path)
    if path.is_absolute():
        return path.as_posix()
    return (image_root / path).as_posix()
