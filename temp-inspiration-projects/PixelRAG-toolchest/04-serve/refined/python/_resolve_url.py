def _resolve_url(article_id: int) -> str:
    """Resolve URL or title from article_id."""
    articles = _state["articles"]
    if article_id < len(articles):
        entry = articles[article_id]
        if isinstance(entry, dict):
            return entry.get("url") or entry.get("title", "")
        return str(entry)
    return ""
