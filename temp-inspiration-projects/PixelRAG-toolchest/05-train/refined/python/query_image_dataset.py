class QueryImageDataset(Dataset):
    """Dataset of (query, positive_path, [negative_paths...]) from JSONL.

    Supports two formats:
    - Simple: {"query": "...", "chunk_path": "..."}
    - Hard negatives: {"query": "...", "chunk_path": "...", "neg_chunk_paths": ["...", ...]}

    Pre-validates all images at init time so every __getitem__ is guaranteed
    to succeed — critical for DDP where all ranks must process the same
    number of batches (a None/skipped batch on one rank deadlocks NCCL).
    """

    def __init__(
        self,
        jsonl_path,
        max_pairs=None,
        num_hard_negatives=0,
        skip_image_verify=False,
        reverse=False,
    ):
        self.pairs = []  # (query, pos_path, [neg_path1, neg_path2, ...])
        self.num_hard_negatives = num_hard_negatives
        jsonl_dir = Path(jsonl_path).resolve().parent
        skipped = 0

        def _resolve_path(path_str):
            path = Path(path_str)
            if path.is_absolute():
                return str(path)
            return str((jsonl_dir / path).resolve())

        with open(jsonl_path) as f:
            for line in f:
                item = json.loads(line)
                pos_path = _resolve_path(item["chunk_path"])
                if not os.path.exists(pos_path):
                    skipped += 1
                    continue
                if not skip_image_verify:
                    try:
                        with Image.open(pos_path) as im:
                            im.convert("RGB").verify()
                    except Exception as e:
                        logger.warning(f"Bad image {pos_path}: {e}")
                        skipped += 1
                        continue

                # Collect hard negatives if present (path-check only, no image verify)
                neg_paths = []
                if num_hard_negatives > 0 and "neg_chunk_paths" in item:
                    for np_ in item["neg_chunk_paths"][:num_hard_negatives]:
                        np_ = _resolve_path(np_)
                        if os.path.exists(np_):
                            neg_paths.append(np_)
                    # Pad with None if not enough negatives (will be skipped in collate)
                    while len(neg_paths) < num_hard_negatives:
                        neg_paths.append(None)

                self.pairs.append((item["query"], pos_path, neg_paths))
        if reverse:
            self.pairs.reverse()
            logger.info("Reversed data order (high-quality-first curriculum)")
        if max_pairs:
            self.pairs = self.pairs[:max_pairs]
        if skipped:
            logger.warning(f"Skipped {skipped} missing/bad images at init")
        n_with_negs = sum(
            1 for _, _, negs in self.pairs if any(n is not None for n in negs)
        )
        logger.info(
            f"Loaded {len(self.pairs)} valid pairs from {jsonl_path}"
            + (
                f" ({n_with_negs} with hard negatives)"
                if num_hard_negatives > 0
                else ""
            )
        )

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        return self.pairs[idx]
