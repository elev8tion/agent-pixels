def resolve_editorial_photo(
    row: dict, livevqa_images: str = LIVEVQA_IMAGES_DIR
) -> str | None:
    """Return the path to the editorial photo for a QA row, or None."""
    ip = row.get("img_path")
    if not ip:
        return None
    full = os.path.join(livevqa_images, ip)
    return full if os.path.exists(full) else None
