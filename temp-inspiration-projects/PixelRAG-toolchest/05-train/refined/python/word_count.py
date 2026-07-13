def word_count(query: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", query))
