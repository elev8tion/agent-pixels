def batch_retrieve_pixel(
    queries: list[dict],
    api_url: str,
    search_k: int = 50,
    top_k: int = 10,
    batch_size: int = 16,
    nprobe: int | None = None,
    timeout: int = 180,
    db_path: str = "/opt/dlami/nvme/news_pages/state.db",
) -> list[list[dict]]:
    """Batch pixel retrieval via news tile search API.

    Returns a list (one per query) of lists of hit dicts with keys:
    hex, file, tile, chunk, score.
    """
    # Build url-to-hex mapping from news DB
    url_to_hex: dict[str, str] = {}
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, url FROM articles WHERE status = 'downloaded'")
        url_to_hex = {row[1]: row[0] for row in cur}
        conn.close()
        logger.info("Loaded url->hex map: %d entries from %s", len(url_to_hex), db_path)

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
                hex_id = url_to_hex.get(url)
                if not hex_id:
                    continue
                if len(items) >= top_k:
                    break
                items.append(
                    {
                        "hex": hex_id,
                        "file": os.path.basename(hit.get("path", "")),
                        "tile": int(hit.get("tile_index", 0)),
                        "chunk": int(hit.get("chunk_index", 0)),
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
                "Pixel retrieval batch %d/%d  done=%d  %.1f q/s  last=%.2fs  ETA=%.0fs",
                batch_num,
                n_batches,
                done,
                qps,
                dt,
                eta,
            )

    return all_results
