def resolve_text_context(
    row: dict,
    retrieved_items: list[dict],
    top_k: int,
    include_photo: bool,
    livevqa_images: str,
    chunks_db: str | None = None,
    hex_to_int: dict | None = None,
    url_to_hex: dict | None = None,
) -> tuple[list[str] | None, list[str], str]:
    """Build text passages and prompt for text reader mode.

    For text retrieval items (with 'text' key), uses text directly.
    For pixel retrieval items (cross-format), looks up text from DB.

    Returns (image_paths_or_None, passages, prompt_text).
    """
    photo = resolve_editorial_photo(row, livevqa_images) if include_photo else None
    passages: list[str] = []

    for it in retrieved_items[:top_k]:
        if "text" in it and it["text"]:
            passages.append(it["text"])
        elif chunks_db and hex_to_int:
            # Cross-format: pixel retrieval item, fetch text from DB
            hex_id = it.get("hex", "")
            if not hex_id and url_to_hex:
                hex_id = url_to_hex.get(it.get("url", ""), "")
            if hex_id and hex_id in hex_to_int:
                aid = hex_to_int[hex_id]
                ci = int(it.get("chunk", it.get("chunk_index", 0)))
                # Thread-local connection handled by caller
                text = _fetch_chunk_text(chunks_db, aid, ci)
                if text:
                    passages.append(text)

    imgs = [photo] if photo else None
    prompt = build_text_prompt(
        row["question"], row["options"], passages, has_photo=bool(photo)
    )
    return imgs, passages, prompt
