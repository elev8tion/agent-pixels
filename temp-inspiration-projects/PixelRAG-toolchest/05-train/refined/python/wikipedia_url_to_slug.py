def wikipedia_url_to_slug(url):
    """Normalize an enwiki URL to an article slug."""
    if not url or "/wiki/" not in url:
        return None
    slug = unquote(url.split("/wiki/")[-1]).replace(" ", "_").split("#")[0]
    if not slug or slug.startswith("Category:"):
        return None
    return slug
