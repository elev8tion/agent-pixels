def load_slug_to_article_id(articles_json):
    """Load articles.json and build slug -> article_id map."""
    with open(articles_json) as f:
        articles = json.load(f)
    return {slug: idx for idx, slug in enumerate(articles)}
