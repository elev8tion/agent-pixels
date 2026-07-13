def is_informative_page(entry: dict) -> bool:
    if entry.get("page_height", 0) < 3000:
        return False
    if entry.get("num_tiles", 0) < 1:
        return False
    if not entry.get("complete", False):
        return False

    title_lower = entry["title"].lower()
    url_lower = entry.get("url", "").lower()
    check = title_lower + " " + url_lower

    for pat in SKIP_RE:
        if pat.search(check):
            return False
    for pat in SKIP_CONTENT_RE:
        if pat.search(check):
            return False

    return True
