def filter_selected_pages_by_chunk_count(
    pages: list[dict],
    tiles_root: Path,
    min_page_chunks: int | None = None,
    max_page_chunks: int | None = None,
) -> list[dict]:
    if min_page_chunks is None and max_page_chunks is None:
        return pages

    kept = []
    for entry in pages:
        chunk_count = get_page_chunk_count(entry, tiles_root)
        if min_page_chunks is not None and chunk_count < min_page_chunks:
            continue
        if max_page_chunks is not None and chunk_count > max_page_chunks:
            continue
        kept.append(entry)
    return kept
