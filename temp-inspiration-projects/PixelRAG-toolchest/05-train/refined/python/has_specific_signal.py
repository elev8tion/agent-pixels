def has_specific_signal(query):
    return any(p.search(query) for p in SPECIFIC_RE)
