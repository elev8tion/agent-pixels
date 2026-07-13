def process_split(
    split_name: str,
    jsonl_path: Path,
    out_path: Path,
    api_url: str,
    batch_size: int,
    n_docs: int,
) -> dict:
    # Resume: count existing lines
    existing = 0
    if out_path.exists():
        with open(out_path) as f:
            for _ in f:
                existing += 1
        print(f"  [{split_name}] resume: {existing} rows already saved")

    examples = []
    with open(jsonl_path) as f:
        for line in f:
            examples.append(json.loads(line))
    total = len(examples)
    print(f"  [{split_name}] total={total}, skipping first {existing}")

    examples = examples[existing:]
    if not examples:
        print(f"  [{split_name}] already complete, skipping")
        return _collect_stats(out_path)

    t0 = time.time()
    n_done = existing
    gold_in_topk = {1: 0, 3: 0, 6: 0}
    gold_miss = 0

    # Re-scan existing for stats
    if out_path.exists():
        with open(out_path) as f:
            for line in f:
                r = json.loads(line)
                pos = r.get("gold_in_top6_pos", -1)
                if pos < 0:
                    gold_miss += 1
                else:
                    for k in (1, 3, 6):
                        if pos < k:
                            gold_in_topk[k] += 1

    with open(out_path, "a") as out_f:
        for i in range(0, len(examples), batch_size):
            batch = examples[i : i + batch_size]
            queries = [ex["query"] for ex in batch]
            try:
                results = search_batch(api_url, queries, n_docs=n_docs)
            except Exception as e:
                print(f"  [{split_name}] FATAL at batch {i}: {e}", file=sys.stderr)
                raise

            for ex, res in zip(batch, results):
                gold_rel = ex["chunk_path"]
                gs = shard_suffix(gold_rel)
                hits = res.get("hits", [])
                hit_sufs = [shard_suffix(h["path"]) for h in hits]
                try:
                    pos = hit_sufs.index(gs)
                except ValueError:
                    pos = -1

                if pos < 0:
                    gold_miss += 1
                else:
                    for k in (1, 3, 6):
                        if pos < k:
                            gold_in_topk[k] += 1

                # Keep only fields we need per hit
                trimmed = [
                    {
                        "path": h["path"],
                        "score": h.get("score"),
                        "article_id": h.get("article_id"),
                        "url": h.get("url"),
                    }
                    for h in hits
                ]

                row = {
                    "query": ex["query"],
                    "answer": ex["answer"],
                    "gold_path_rel": gold_rel,
                    "gold_suffix": gs,
                    "hits": trimmed,
                    "gold_in_top6_pos": pos,
                }
                out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
            out_f.flush()

            n_done += len(batch)
            batch_idx = i // batch_size
            if batch_idx % 5 == 0 or n_done == total:
                el = time.time() - t0
                rate = (n_done - existing) / max(el, 1e-9)
                eta = (total - n_done) / max(rate, 1e-9) / 60
                print(
                    f"  [{split_name}] {n_done}/{total} "
                    f"({rate:.1f} q/s, eta {eta:.1f} min) "
                    f"gold@1={gold_in_topk[1] / max(1, n_done) * 100:.1f}% "
                    f"gold@3={gold_in_topk[3] / max(1, n_done) * 100:.1f}% "
                    f"gold@6={gold_in_topk[6] / max(1, n_done) * 100:.1f}% "
                    f"miss={gold_miss / max(1, n_done) * 100:.1f}%"
                )

    return {
        "split": split_name,
        "total": n_done,
        "gold_in_top1": gold_in_topk[1],
        "gold_in_top3": gold_in_topk[3],
        "gold_in_top6": gold_in_topk[6],
        "gold_miss": gold_miss,
    }
