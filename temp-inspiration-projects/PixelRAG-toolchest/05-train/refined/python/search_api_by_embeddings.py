def search_api_by_embeddings(search_api_url, query_embeddings, n_docs=3, timeout=120):
    """Search the wiki-screenshot index using pre-computed query embeddings."""
    if query_embeddings.ndim != 2:
        raise ValueError(
            f"Expected 2D query embeddings, got shape={query_embeddings.shape}"
        )
    payload = {
        "queries": [{"embedding": emb.tolist()} for emb in query_embeddings],
        "n_docs": n_docs,
    }
    req = urlrequest.Request(
        search_api_url.rstrip("/") + "/search",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urlerror.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Search API HTTP {e.code}: {body}") from e
    except urlerror.URLError as e:
        raise RuntimeError(f"Search API request failed: {e}") from e
