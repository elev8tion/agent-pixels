def resolve_pixel_context(
    row: dict,
    retrieved_items: list[dict],
    top_k: int,
    include_photo: bool,
    livevqa_images: str,
    tiles_dir: str,
) -> tuple[list[str], str]:
    """Build image paths and prompt for pixel reader mode.

    Returns (image_paths, prompt_text).
    """
    images: list[str] = []
    photo = resolve_editorial_photo(row, livevqa_images) if include_photo else None
    if photo:
        images.append(photo)
    for it in retrieved_items[:top_k]:
        p = resolve_strip_path(it["hex"], it["file"], tiles_dir)
        if p:
            images.append(p)
    prompt = build_pixel_prompt(row["question"], row["options"], has_photo=bool(photo))
    return images, prompt
