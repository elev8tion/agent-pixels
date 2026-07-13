def _get_urls_from_metadata(example: dict) -> list[str]:
    """Extract all URLs from example metadata.

    Supports both SimpleQA format (metadata as string) and SimpleQA Verified format (metadata as dict or string).
    """
    meta = example.get("metadata")

    # If metadata is already a dict (SimpleQA Verified format)
    if isinstance(meta, dict):
        urls = meta.get("urls", [])
        if isinstance(urls, list):
            return urls
        return []

    # If metadata is a string (SimpleQA format or SimpleQA Verified string format)
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except json.JSONDecodeError:
            try:
                meta = ast.literal_eval(meta)
            except (ValueError, SyntaxError):
                return []

    if isinstance(meta, dict) and "urls" in meta:
        urls = meta["urls"]
        if isinstance(urls, list):
            return urls
    return []
