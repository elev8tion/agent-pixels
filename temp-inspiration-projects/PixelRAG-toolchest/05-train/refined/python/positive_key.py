def positive_key(row: dict) -> tuple[int | None, int | None]:
    article_id = row.get("article_id")
    chunk_index = row.get("chunk_index")
    return article_id, chunk_index
