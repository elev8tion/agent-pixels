def normalize_hit(hit: dict, rank: int) -> dict:
    return {
        "rank": rank + 1,
        "score": hit.get("score", 0.0),
        "article_id": hit.get("article_id"),
        "chunk_index": hit.get("chunk_index"),
        "char_offset": hit.get("char_offset"),
        "n_tokens": hit.get("n_tokens"),
        "title": hit.get("title"),
        "url": hit.get("url"),
        "text": hit.get("text", ""),
    }
