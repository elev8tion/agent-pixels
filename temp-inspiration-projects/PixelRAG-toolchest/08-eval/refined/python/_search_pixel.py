def _search_pixel(query: str, n_docs: int | None = None) -> list[dict]:
    """Return top-K screenshot tiles as multimodal content parts."""
    if n_docs is None:
        n_docs = _DEFAULT_TOP_K
    n_docs = max(1, min(n_docs, _MAX_TOP_K))
    body = {"queries": [{"text": query}], "n_docs": n_docs}
    req = urllib.request.Request(
        _PIXEL_API,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=SEARCH_TIMEOUT) as resp:
            d = json.load(resp)
        hits = d.get("results", [{}])[0].get("hits", [])
    except Exception as e:
        return [{"type": "text", "text": f"[search_error: {e}]"}]

    if not hits:
        return [{"type": "text", "text": "[no results]"}]

    parts: list[dict] = [{"type": "text", "text": "Top-K Wikipedia screenshot tiles:"}]
    for h in hits:
        png_path = h.get("path", "")
        try:
            with open(png_path, "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode("ascii")
            parts.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64}",
                        "detail": _IMAGE_DETAIL,
                    },
                }
            )
        except Exception as e:
            parts.append({"type": "text", "text": f"[image_error for {png_path}: {e}]"})
    return parts
