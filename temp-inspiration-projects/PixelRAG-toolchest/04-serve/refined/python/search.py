@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    t0 = time.time()

    # Encode queries
    if req.queries and all(q.embedding is not None for q in req.queries):
        query_vectors = _normalize_query_embeddings(req.queries)
    else:
        if any(q.embedding is not None for q in req.queries):
            raise HTTPException(
                status_code=400,
                detail="Do not mix pre-computed embeddings with text/image queries in one request.",
            )
        query_vectors = _encode_queries(req.queries, req.instruction)
    t_encode = time.time() - t0

    # FAISS search
    index = _state["index"]
    default_nprobe = index.nprobe
    if req.nprobe is not None:
        index.nprobe = req.nprobe

    # Over-fetch when filtering to ensure enough results after filtering.
    # Meta pages can be the majority of raw hits, so articles_only needs more.
    if req.articles_only:
        fetch_k = req.n_docs * 10
    elif req.min_tile_height:
        fetch_k = req.n_docs * 5
    else:
        fetch_k = req.n_docs
    distances, indices = index.search(query_vectors, fetch_k)

    if req.nprobe is not None:
        index.nprobe = default_nprobe
    t_search = time.time() - t0 - t_encode

    # Build results
    meta = _state["metadata"]
    article_ids = meta["article_ids"]
    tile_indices = meta["tile_indices"]
    chunk_indices = meta["chunk_indices"]
    y_offsets = meta["y_offsets"]
    tile_heights = meta["tile_heights"]
    tiles_dir = _state.get("tiles_dir", "")

    results = []
    for qi in range(len(req.queries)):
        hits = []
        for j in range(fetch_k):
            vid = int(indices[qi, j])
            if vid == -1:
                continue
            th = int(tile_heights[vid])
            if req.min_tile_height and th < req.min_tile_height:
                continue
            aid = int(article_ids[vid])
            url = _resolve_url(aid)
            if req.articles_only and _is_meta(url):
                continue
            ti = int(tile_indices[vid])
            ci = int(chunk_indices[vid])
            tile_path = _resolve_path(aid, ti, ci)
            img_b64 = None
            if req.include_images and tile_path and os.path.exists(tile_path):
                with open(tile_path, "rb") as fp:
                    img_b64 = base64.b64encode(fp.read()).decode()
            elif req.include_images and _state.get("ondemand") is not None:
                img_b64 = _ondemand_chunk_b64(aid, ti, ci, th)
            # Expose a relative tile path, not the absolute server filesystem
            # path (avoids leaking the host's directory layout; clients fetch
            # tiles via /tile/{article_id}/{tile_index}/{chunk_index}).
            rel_path = tile_path
            if tiles_dir:
                candidate = os.path.relpath(tile_path, tiles_dir)
                if not candidate.startswith(".."):
                    rel_path = candidate
            hits.append(
                Hit(
                    score=float(distances[qi, j]),
                    vector_id=vid,
                    article_id=aid,
                    tile_index=ti,
                    chunk_index=ci,
                    y_offset=int(y_offsets[vid]),
                    tile_height=th,
                    path=rel_path,
                    url=url,
                    article_pages=_article_pages(aid),
                    image_base64=img_b64,
                )
            )
            if len(hits) >= req.n_docs:
                break
        results.append(QueryResult(hits=hits))

    logger.info(
        "Search: %d queries, n_docs=%d, encode=%.3fs, search=%.3fs, total=%.3fs",
        len(req.queries),
        req.n_docs,
        t_encode,
        t_search,
        time.time() - t0,
    )

    return SearchResponse(results=results)
