def _is_meta(url: str) -> bool:
    return bool(_META_RE.search(url))
