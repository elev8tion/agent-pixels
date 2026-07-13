class TextQueryDataset(Dataset):
    """Dataset of (query, positive_text, [negative_texts...]) from text-qa-pair JSONL.

    Each row has: query, passage (positive), neg_passages (list of hard negative texts).
    """

    def __init__(self, jsonl_paths, max_pairs=None, num_hard_negatives=0):
        self.pairs = []
        self.num_hard_negatives = num_hard_negatives
        skipped = 0

        for jsonl_path in (
            jsonl_paths if isinstance(jsonl_paths, list) else [jsonl_paths]
        ):
            with open(jsonl_path) as f:
                for line in f:
                    item = json.loads(line)
                    if "passage" not in item or not item["passage"]:
                        skipped += 1
                        continue

                    neg_texts = []
                    if num_hard_negatives > 0 and "neg_passages" in item:
                        for nt in item["neg_passages"][:num_hard_negatives]:
                            if nt:
                                neg_texts.append(nt)
                        while len(neg_texts) < num_hard_negatives:
                            neg_texts.append(item["passage"])  # pad with positive

                    self.pairs.append((item["query"], item["passage"], neg_texts))
                    if max_pairs and len(self.pairs) >= max_pairs:
                        break
            if max_pairs and len(self.pairs) >= max_pairs:
                break

        logger.info(
            f"Loaded {len(self.pairs)} text pairs from {jsonl_paths} "
            f"(skipped {skipped})"
        )

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        return self.pairs[idx]
