def _collect_stats(path: Path) -> dict:
    gold_in_topk = {1: 0, 3: 0, 6: 0}
    gold_miss = 0
    n = 0
    if path.exists():
        with open(path) as f:
            for line in f:
                r = json.loads(line)
                n += 1
                pos = r.get("gold_in_top6_pos", -1)
                if pos < 0:
                    gold_miss += 1
                else:
                    for k in (1, 3, 6):
                        if pos < k:
                            gold_in_topk[k] += 1
    return {
        "split": path.stem,
        "total": n,
        "gold_in_top1": gold_in_topk[1],
        "gold_in_top3": gold_in_topk[3],
        "gold_in_top6": gold_in_topk[6],
        "gold_miss": gold_miss,
    }
