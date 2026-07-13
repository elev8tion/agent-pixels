def build_variable_image_set(row: dict, rng: random.Random, k_min: int, k_max: int):
    """Sample k ~ Uniform[k_min, k_max], return (shard_suffixes, gold_pos, k)."""
    gold = row["gold_suffix"]
    hit_sufs = [shard_suffix(h["path"]) for h in row["hits"]]
    non_gold = [s for s in hit_sufs if s != gold]
    k = rng.randint(k_min, k_max)
    chosen = [gold] + non_gold[: k - 1]
    while len(chosen) < k:
        chosen.append(gold)
    idx = list(range(k))
    rng.shuffle(idx)
    shuffled = [chosen[i] for i in idx]
    gold_pos = idx.index(0)
    return shuffled, gold_pos, k
