def load_text_cache(cache_path: str) -> dict:
    """Load pre-fetched text from JSONL file.

    Args:
        cache_path: Path to JSONL file with cached text.

    Returns:
        Dict mapping example ID to cached item.
    """
    logger.info(f"Loading text cache from {cache_path}...")
    cache = {}
    with open(cache_path, "r") as f:
        for line in f:
            item = json.loads(line)
            cache[item["id"]] = item
    logger.info(f"Loaded {len(cache)} cached items.")
    return cache
