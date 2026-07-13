@functools.lru_cache(maxsize=8192)
def _article_pages(article_id: int) -> str | None:
    """Map of chunk files that exist on disk for an article: "0:0-8,1:0-4".

    Lets clients (notably the chat agent) page through an article without
    probing nonexistent coordinates. Returns None when tiles are rendered
    on demand (no files on disk) or the article dir can't be found.
    """
    if _state.get("ondemand") is not None:
        return None
    probe = _resolve_path(article_id, 0, 0)
    d = os.path.dirname(probe)
    if not os.path.isdir(d):
        return None
    tiles: dict[int, list[int]] = {}
    for name in os.listdir(d):
        m = re.match(r"chunk_(\d{4})_(\d{2})\.(?:png|jpg|jpeg)$", name)
        if m:
            tiles.setdefault(int(m.group(1)), []).append(int(m.group(2)))
    if not tiles:
        return None
    return ",".join(f"{t}:{min(cs)}-{max(cs)}" for t, cs in sorted(tiles.items()))
