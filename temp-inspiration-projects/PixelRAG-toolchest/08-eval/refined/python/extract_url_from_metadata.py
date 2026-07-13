def extract_url_from_metadata(example: dict) -> str | None:
    """Extract URL from example metadata.

    Args:
        example: Example dict with 'metadata' field.

    Returns:
        Extracted URL or None.
    """
    meta = example.get("metadata")
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except json.JSONDecodeError:
            try:
                meta = ast.literal_eval(meta)
            except (ValueError, SyntaxError):
                pass

    target_url = None
    if isinstance(meta, dict):
        if "url" in meta:
            target_url = meta["url"]
        elif (
            "urls" in meta and isinstance(meta["urls"], list) and len(meta["urls"]) > 0
        ):
            # Flatten URLs: some entries have multiple URLs concatenated in a single string
            # (separated by newlines OR directly joined like "https://a.comhttps://b.com")
            all_urls = []
            for url_entry in meta["urls"]:
                if isinstance(url_entry, str):
                    # Split on "https://" boundaries to handle concatenated URLs
                    parts = re.split(r"(?=https?://)", url_entry)
                    for part in parts:
                        part = part.strip().rstrip(",'\"").strip("- ").strip()
                        if part and re.match(r"https?://", part):
                            all_urls.append(part)

            # Prefer en.wikipedia.org article URLs (exclude non-English and Category pages)
            wikipedia_urls = [
                u
                for u in all_urls
                if "en.wikipedia.org/wiki/" in u
                and "/Category:" not in u
                and "wikipedia-on-ipfs" not in u.lower()
            ]
            if wikipedia_urls:
                target_url = wikipedia_urls[0]
            else:
                # Secondary: wikimedia.org URLs (e.g., commons.wikimedia.org)
                wikimedia_urls = [u for u in all_urls if "wikimedia.org" in u.lower()]
                target_url = (
                    wikimedia_urls[0]
                    if wikimedia_urls
                    else (all_urls[0] if all_urls else None)
                )

    # Extract first valid URL from the string
    if target_url:
        url_match = re.search(r"https?://[^\s<>\"{}|\\^`\[\]]+", target_url)
        target_url = url_match.group(0) if url_match else None

    # Note by Yichuan: strip URL fragment (#section) so that URLs differing
    # only by anchor are treated as the same page for deduplication and
    # retrieval-accuracy matching.
    if target_url and "#" in target_url:
        target_url = target_url.split("#")[0]

    return target_url
