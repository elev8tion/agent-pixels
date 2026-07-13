def article_url(article: dict) -> str:
    """Get navigate URL for an article. Supports both file:// and http://."""
    f = article["file"]
    return f if f.startswith("http") else f"file://{f}"
