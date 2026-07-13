def collect_paths(retrieval_dir: Path, splits: list[str]) -> set[str]:
    """Collect every unique absolute path across hit lists + gold suffixes.

    Gold paths use the dataset-relative form ('images/shard_.../chunk.png');
    hits are absolute '/opt/dlami/nvme/kiwix_tiles/shard_.../chunk.png'.
    We normalize everything to shard-suffix for dedup across sources.
    Returns set of (shard_suffix_key, preferred_abs_path_for_fetch).
    """
    by_suffix = {}
    for split in splits:
        p = retrieval_dir / f"{split}.jsonl"
        if not p.exists():
            print(f"  missing: {p}")
            continue
        with open(p) as f:
            for line in f:
                r = json.loads(line)
                # gold (will fall back to local if possible)
                gs = r["gold_suffix"]
                if gs not in by_suffix:
                    by_suffix[gs] = None  # local-resolvable
                # hits (absolute)
                for h in r["hits"]:
                    ss = shard_suffix(h["path"])
                    if ss not in by_suffix or by_suffix[ss] is None:
                        by_suffix[ss] = h["path"]
    return by_suffix
