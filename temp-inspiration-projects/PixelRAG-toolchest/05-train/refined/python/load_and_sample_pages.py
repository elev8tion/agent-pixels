def load_and_sample_pages(
    index_path: Path,
    n: int,
    batch_index: int = 0,
    total_batches: int = 1,
) -> list:
    MASTER_SEED = 0
    print(f"Loading index from {index_path}...")
    candidates: list = []

    with open(index_path) as f:
        for line in f:
            entry = json.loads(line)
            if is_informative_page(entry):
                candidates.append(entry)

    print(f"Total eligible: {len(candidates):,} pages")

    rng = random.Random(MASTER_SEED)
    rng.shuffle(candidates)

    slice_size = len(candidates) // total_batches
    start = batch_index * slice_size
    end = start + slice_size if batch_index < total_batches - 1 else len(candidates)
    pool = candidates[start:end]

    print(
        f"Batch {batch_index}/{total_batches}: pages [{start}:{end}] ({len(pool):,} in pool)"
    )
    selected = pool[:n] if n <= len(pool) else pool
    return selected
