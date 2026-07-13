def execute_pixelrag_search(
    query: str, n_results: int = 5, endpoint: str = "http://localhost:30001"
) -> dict:
    """Call the PixelRAG search API."""
    body = json.dumps(
        {"queries": [{"text": query}], "n_docs": min(n_results, 20)}
    ).encode()
    req = urllib.request.Request(
        f"{endpoint}/search",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    hits = data.get("results", [{}])[0].get("hits", [])
    results = []
    for hit in hits:
        url = hit.get("url", "")
        slug = url.split("/wiki/")[-1] if "/wiki/" in url else ""
        title = slug.replace("_", " ") if slug else url
        results.append(
            {
                "title": title,
                "url": url,
                "score": round(hit["score"], 4),
                "tile": f"tile_{hit.get('tile_index', '?')}_chunk_{hit.get('chunk_index', '?')}",
            }
        )
    return {"query": query, "results": results, "count": len(results)}
