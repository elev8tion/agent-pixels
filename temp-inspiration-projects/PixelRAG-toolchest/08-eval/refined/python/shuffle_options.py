def shuffle_options(
    options: list[str], ground_truth: str, seed: int
) -> tuple[list[str], str]:
    """Shuffle option order with a deterministic seed; return (new_options, new_gt_letter)."""
    rng = random.Random(seed)
    texts = [opt.split(". ", 1)[1] if ". " in opt else opt for opt in options]
    gt_idx = LETTERS.index(ground_truth)
    indices = list(range(len(texts)))
    rng.shuffle(indices)
    new_options = [f"{LETTERS[i]}. {texts[indices[i]]}" for i in range(len(indices))]
    new_gt_idx = indices.index(gt_idx)
    return new_options, LETTERS[new_gt_idx]
