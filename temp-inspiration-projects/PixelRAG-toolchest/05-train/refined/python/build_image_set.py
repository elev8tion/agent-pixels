def build_image_set(row: dict, seed_base: int, n_images: int) -> tuple[list[str], int]:
    """Return (list of n_images shard-suffixes, gold index) with gold position shuffled.
    Composition: gold + (n_images-1) non-gold hits from top-6."""
    gold = row["gold_suffix"]
    hit_sufs = [shard_suffix(h["path"]) for h in row["hits"]]
    non_gold = [s for s in hit_sufs if s != gold]
    chosen = [gold] + non_gold[: n_images - 1]
    while len(chosen) < n_images:
        chosen.append(gold)
    rng = random.Random(seed_base)
    idx = list(range(n_images))
    rng.shuffle(idx)
    shuffled = [chosen[i] for i in idx]
    gold_pos = idx.index(0)
    return shuffled, gold_pos
