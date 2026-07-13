def is_bad_title(title: str) -> bool:
    check = (title or "").strip().lower()
    if not check:
        return True
    for pat in SKIP_RE:
        if pat.search(check):
            return True
    for pat in SKIP_CONTENT_RE:
        if pat.search(check):
            return True
    return False
