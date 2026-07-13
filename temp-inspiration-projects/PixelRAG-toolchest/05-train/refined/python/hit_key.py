def hit_key(hit: dict) -> tuple[int | None, int | None]:
    return hit.get("article_id"), hit.get("chunk_index")
