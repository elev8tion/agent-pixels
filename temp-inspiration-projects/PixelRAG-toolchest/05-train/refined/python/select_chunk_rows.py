def select_chunk_rows(
    db_path: Path,
    articles: list[dict],
    seed: int,
    min_paragraph_words: int,
) -> list[dict]:
    rng = random.Random(seed)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    work_items = []

    for article in articles:
        usable_chunk_count = max(1, int(article["n_chunks"] * 0.7))
        candidate_indices = list(range(usable_chunk_count))
        rng.shuffle(candidate_indices)

        selected_row = None
        for chunk_index in candidate_indices[: min(len(candidate_indices), 5)]:
            row = cur.execute(
                """
                SELECT text, char_offset, n_tokens
                FROM chunks
                WHERE article_id = ? AND chunk_index = ?
                """,
                (article["article_id"], chunk_index),
            ).fetchone()
            if not row:
                continue
            text, char_offset, n_tokens = row
            if not is_candidate_passage(text, n_tokens):
                continue
            focus_paragraph = extract_best_long_paragraph(
                text, min_paragraph_words=min_paragraph_words
            )
            if not focus_paragraph:
                continue
            title = infer_title(text)
            selected_row = {
                "article_id": article["article_id"],
                "article_n_chunks": article["n_chunks"],
                "article_text_length": article["text_length"],
                "chunk_index": chunk_index,
                "char_offset": char_offset,
                "n_tokens": n_tokens,
                "title_guess": title,
                "focus_paragraph": focus_paragraph,
                "passage": text,
            }
            break

        if selected_row:
            work_items.append(selected_row)

    conn.close()
    return work_items
