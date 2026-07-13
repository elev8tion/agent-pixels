def load_candidate_articles(
    db_path: Path,
    num_articles: int,
    batch_index: int,
    total_batches: int,
    min_article_chunks: int,
    max_article_chunks: int | None,
) -> list[dict]:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    query = """
        SELECT article_id, n_chunks, text_length
        FROM articles
        WHERE status = 'extracted'
          AND n_chunks >= ?
    """
    params: list[int] = [min_article_chunks]
    if max_article_chunks is not None:
        query += "\n          AND n_chunks <= ?"
        params.append(max_article_chunks)
    rows = list(cur.execute(query, params))
    conn.close()

    candidates = [
        {"article_id": article_id, "n_chunks": n_chunks, "text_length": text_length}
        for article_id, n_chunks, text_length in rows
    ]
    print(f"Total eligible articles: {len(candidates):,}")

    rng = random.Random(MASTER_SEED)
    rng.shuffle(candidates)

    slice_size = len(candidates) // total_batches
    start = batch_index * slice_size
    end = start + slice_size if batch_index < total_batches - 1 else len(candidates)
    pool = candidates[start:end]
    print(
        f"Batch {batch_index}/{total_batches}: articles [{start}:{end}] ({len(pool):,} in pool)"
    )

    selected = pool[:num_articles] if num_articles <= len(pool) else pool
    return selected
