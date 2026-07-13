def compute_query_stats(queries: list[str]) -> dict:
    if not queries:
        return {
            "count": 0,
            "avg_words": 0.0,
            "avg_chars": 0.0,
            "top_starts": [],
            "has_quote_pct": 0.0,
            "has_year_pct": 0.0,
        }

    starts = Counter(question_start_bucket(query) for query in queries)
    word_counts = [word_count(query) for query in queries]
    char_counts = [len(query) for query in queries]
    has_quote = sum('"' in query or "'" in query for query in queries)
    has_year = sum(
        bool(re.search(r"\b(1[0-9]{3}|20[0-2][0-9])\b", query)) for query in queries
    )
    return {
        "count": len(queries),
        "avg_words": round(sum(word_counts) / len(word_counts), 2),
        "avg_chars": round(sum(char_counts) / len(char_counts), 2),
        "top_starts": starts.most_common(12),
        "has_quote_pct": round(100 * has_quote / len(queries), 2),
        "has_year_pct": round(100 * has_year / len(queries), 2),
    }
