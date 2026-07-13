def has_generic_signal(query):
    return any(p.search(query) for p in GENERIC_STRONG_RE)
