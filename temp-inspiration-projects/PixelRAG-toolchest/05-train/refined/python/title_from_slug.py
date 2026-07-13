def title_from_slug(slug: str) -> str:
    """Convert URL slug to readable title."""
    title = slug.replace("_", " ")
    # Remove URL encoding
    title = re.sub(r"%[0-9A-Fa-f]{2}", " ", title)
    return title.strip()
