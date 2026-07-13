def _search_text(query: str, n_docs: int | None = None) -> str:
    """Return top-K text chunks formatted as one string."""
    if n_docs is None:
        n_docs = _DEFAULT_TOP_K
    n_docs = max(1, min(n_docs, _MAX_TOP_K))
    body = {"queries": [{"text": query}], "n_docs": n_docs}
    req = urllib.request.Request(
        _TEXT_API,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=SEARCH_TIMEOUT) as resp:
            d = json.load(resp)
        hits = d.get("results", [{}])[0].get("hits", [])
    except Exception as e:
        return f"[search_error: {e}]"

    if not hits:
        return "[no results]"

    parts = []
    for h in hits:
        title = (h.get("title") or "").strip() or h.get("url", "")
        text = (h.get("text") or "").strip()
        chunk_idx = h.get("chunk_index", 0)
        label = f"{title} (chunk {chunk_idx})" if chunk_idx > 0 else title
        parts.append(f"*** Doc title: {label}\n*** Contents:\n{text}")
    return "\n\n".join(parts)
