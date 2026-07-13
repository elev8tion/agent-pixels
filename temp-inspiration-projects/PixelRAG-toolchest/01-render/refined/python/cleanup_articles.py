def cleanup_articles(articles: list[dict]):
    for a in articles:
        if a["file"].startswith("http"):
            continue
        try:
            os.unlink(a["file"])
        except OSError:
            pass
