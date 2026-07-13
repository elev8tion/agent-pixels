def to_relative_image_path(path: str, image_root: Path) -> str:
    rel = Path(path).relative_to(image_root)
    return rel.as_posix()
