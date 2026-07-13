def generate_queries(title: str) -> list[str]:
    """Generate fake queries from article title."""
    return [t.format(title=title) for t in QUERY_TEMPLATES]
