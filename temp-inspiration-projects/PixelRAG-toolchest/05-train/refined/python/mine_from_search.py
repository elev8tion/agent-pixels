def mine_from_search(
    pairs: list[dict],
    search_url: str,
    num_negatives: int = 7,
    n_docs: int = 20,
    batch_size: int = 64,
    search_workers: int = 1,
) -> tuple[list[dict], dict]:
    unique_queries = list(dict.fromkeys(p["query"] for p in pairs))
    query_to_idx = {q: i for i, q in enumerate(unique_queries)}
    logger.info("%d unique queries (from %d pairs)", len(unique_queries), len(pairs))

    query_positives: dict[str, set[tuple[int | None, int | None]]] = {}
    for pair in pairs:
        query_positives.setdefault(pair["query"], set()).add(positive_key(pair))

    all_hits: list[list[dict] | None] = [None] * len(unique_queries)
    batches = []
    for i in range(0, len(unique_queries), batch_size):
        batch_queries = unique_queries[i : i + batch_size]
        batches.append((i, batch_queries, i // batch_size + 1))
    n_batches = len(batches)
    completed = 0

    def run_batch(batch_start: int, batch_queries: list[str], batch_idx: int):
        return (
            batch_start,
            batch_queries,
            batch_idx,
            search_batch(search_url, batch_queries, n_docs=n_docs),
        )

    with ThreadPoolExecutor(max_workers=max(1, search_workers)) as executor:
        futures = {
            executor.submit(run_batch, batch_start, batch_queries, batch_idx): (
                batch_start,
                batch_queries,
                batch_idx,
            )
            for batch_start, batch_queries, batch_idx in batches
        }
        for future in as_completed(futures):
            batch_start, batch_queries, batch_idx = futures[future]
            try:
                _, _, _, batch_hits = future.result()
                for j, hits in enumerate(batch_hits):
                    all_hits[batch_start + j] = hits
            except Exception as exc:
                logger.warning("Batch %d/%d failed: %s", batch_idx, n_batches, exc)
                for j in range(len(batch_queries)):
                    all_hits[batch_start + j] = []
            completed += len(batch_queries)
            if batch_idx % 10 == 0 or completed == len(unique_queries):
                logger.info("  Searched: %d/%d", completed, len(unique_queries))

    query_negatives: dict[str, list[dict]] = {}
    query_metadata: dict[str, dict] = {}
    stats = {
        "total": 0,
        "with_negs": 0,
        "avg_negs": 0.0,
        "avg_pos_rank": 0.0,
        "pos_found_rate": 0.0,
        "pos_recall@1": 0.0,
        "pos_recall@10": 0.0,
        "pos_recall@20": 0.0,
    }
    pos_ranks: list[int] = []

    for q in unique_queries:
        positives = query_positives[q]
        hits = all_hits[query_to_idx[q]] or []
        neg_hits: list[dict] = []
        pos_rank = None
        pos_score = None

        for rank, hit in enumerate(hits):
            hk = hit_key(hit)
            if hk in positives:
                if pos_rank is None:
                    pos_rank = rank
                    pos_score = hit.get("score", 0.0)
                continue
            if len(neg_hits) < num_negatives:
                neg_hits.append(normalize_hit(hit, rank))

        query_negatives[q] = neg_hits
        query_metadata[q] = {
            "retrieve_top20": [
                normalize_hit(hit, rank) for rank, hit in enumerate(hits)
            ],
            "positive_rank": pos_rank + 1 if pos_rank is not None else 0,
            "positive_score": pos_score if pos_score is not None else 0.0,
        }
        stats["total"] += 1
        if neg_hits:
            stats["with_negs"] += 1
        if pos_rank is not None:
            pos_ranks.append(pos_rank)

    output_pairs = []
    for pair in pairs:
        neg_hits = query_negatives.get(pair["query"], [])
        meta = query_metadata.get(pair["query"], {})
        output_pairs.append(
            {
                **pair,
                "neg_hits": neg_hits,
                "neg_passages": [hit.get("text", "") for hit in neg_hits],
                "retrieve_top20": meta.get("retrieve_top20", []),
                "positive_score": meta.get("positive_score", 0.0),
                "positive_rank": meta.get("positive_rank", 0),
            }
        )

    total_queries = len(unique_queries)
    if total_queries > 0:
        stats["avg_negs"] = (
            sum(len(query_negatives[q]) for q in unique_queries) / total_queries
        )
        stats["pos_found_rate"] = len(pos_ranks) / total_queries
        stats["pos_recall@1"] = sum(1 for r in pos_ranks if r == 0) / total_queries
        stats["pos_recall@10"] = sum(1 for r in pos_ranks if r < 10) / total_queries
        stats["pos_recall@20"] = sum(1 for r in pos_ranks if r < 20) / total_queries
    if pos_ranks:
        stats["avg_pos_rank"] = sum(pos_ranks) / len(pos_ranks)

    return output_pairs, stats
