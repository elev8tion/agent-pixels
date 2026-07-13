def fetch_text_for_example(
    example: dict, max_chars: int = 50000, text_cache: dict | None = None
) -> tuple[str | None, str | None]:
    """Fetch text content for a single example.

    Args:
        example: Example dict with metadata containing URL.
        max_chars: Maximum characters to return.
        text_cache: Optional pre-fetched text cache.

    Returns:
        Tuple of (text_content, source_url).
    """
    example_id = example.get("id")

    # Check cache first
    if text_cache and example_id in text_cache:
        cached = text_cache[example_id]
        text = cached.get("text")
        url = cached.get("extracted_url")
        if text:
            return text, url

    # Extract URL and fetch
    target_url = extract_url_from_metadata(example)
    if not target_url:
        return None, None

    text = fetch_webpage_text(target_url, max_chars)
    return text, target_url
