def _fetch_chunk_text(db_path: str, article_int: int, chunk_index: int) -> str | None:
    conn = _get_chunks_conn(db_path)
    cur = conn.execute(
        "SELECT text FROM chunks WHERE article_id = ? AND chunk_index = ?",
        (article_int, int(chunk_index)),
    )
    row = cur.fetchone()
    return row[0] if row else None
