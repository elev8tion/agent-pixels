def question_start_bucket(query: str) -> str:
    q = query.strip().lower()
    for prefix in [
        "what",
        "who",
        "which",
        "when",
        "where",
        "why",
        "how",
        "in which",
        "in what",
        "on what",
        "what is",
        "what was",
    ]:
        if q.startswith(prefix):
            return prefix
    parts = re.findall(r"[a-z0-9']+", q)
    return parts[0] if parts else "<empty>"
