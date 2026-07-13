def batch_retrieve_text(
    queries: list[dict],
    api_url: str,
    search_k: int = 50,
    top_k: int = 10,
    batch_size: int = 16,
    nprobe: int | None = None,
    timeout: int = 180,
) -> list[list[dict]]:
    """Batch text retrieval via news text search API.

    Returns a list (one per query) of lists of hit dicts with keys:
    url, chunk_index, text, score.
    """
    all_results: list[list[dict]] = [[] for _ in queries]
    n_batches = (len(queries) + batch_size - 1) // batch_size
    t_all = time.time()

    for bi in range(0, len(queries), batch_size):
        batch_q = queries[bi : bi + batch_size]
        payload: dict = {"queries": batch_q, "n_docs": search_k}
        if nprobe is not None:
            payload["nprobe"] = nprobe
        t0 = time.time()
        r = requests.post(api_url, json=payload, timeout=timeout)
        r.raise_for_status()
        body = r.json()
        dt = time.time() - t0

        for qi, res in enumerate(body["results"]):
            items: list[dict] = []
            for hit in res["hits"]:
                url = hit.get("url", "")
                if not url:
                    continue
                if len(items) >= top_k:
                    break
                items.append(
                    {
                        "url": url,
                        "chunk_index": int(hit.get("chunk_index", 0)),
                        "text": hit.get("text", ""),
                        "score": float(hit.get("score", 0.0)),
                    }
                )
            all_results[bi + qi] = items

        batch_num = bi // batch_size + 1
        if batch_num == 1 or batch_num % 10 == 0 or batch_num == n_batches:
            done = bi + len(batch_q)
            el = time.time() - t_all
            qps = done / el if el > 0 else 0
            eta = (len(queries) - done) / qps if qps > 0 else 0
            logger.info(
                "Text retrieval batch %d/%d  done=%d  %.1f q/s  last=%.2fs  ETA=%.0fs",
                batch_num,
                n_batches,
                done,
                qps,
                dt,
                eta,
            )

    return all_results
