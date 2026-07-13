def _hits_to_retrieval_result(hits: list[dict]) -> "RetrievalResult":  # noqa: F821
    """Convert API hits to RetrievalResult (same logic as LocalAPIRetriever)."""
    from lib.retrieval import RetrievalResult

    if not hits:
        return RetrievalResult(retrieval_type="local_api_react")
    images = []
    image_urls = []
    urls = []
    seen_urls = set()
    for hit in hits:
        path = hit.get("path", "")
        score = hit.get("score", 0.0)
        url = hit.get("url", "")
        if path and os.path.exists(path):
            images.append((path, score))
            image_urls.append(url or None)
        if url and url not in seen_urls:
            seen_urls.add(url)
            urls.append(url)
    return RetrievalResult(
        images=images,
        image_urls=image_urls,
        source_url=", ".join(urls) if urls else None,
        retrieval_type="local_api_react",
    )
