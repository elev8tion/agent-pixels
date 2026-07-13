def chunk_dir(base: Path, start: int, end: int) -> Path:
    return base / f"chunk_{start:06d}_{end:06d}"
