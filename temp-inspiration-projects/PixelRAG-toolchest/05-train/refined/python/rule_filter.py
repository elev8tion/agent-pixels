def rule_filter(record):
    """Returns 'keep', 'remove', or 'classify'."""
    page, chunk = parse_chunk_position(record["chunk_path"])
    query = record["query"].strip()

    # Deep chunks → auto-keep (answer must be in specific section)
    if page >= 1 or chunk >= 5:
        return "keep"

    # Obviously generic queries → auto-remove
    for pat in GENERIC_RE:
        if pat.search(query):
            return "remove"

    # Very short queries are usually generic
    if len(query.split()) < 5:
        return "remove"

    return "classify"
