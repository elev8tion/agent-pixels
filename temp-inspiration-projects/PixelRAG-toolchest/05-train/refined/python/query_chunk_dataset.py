class QueryChunkDataset(Dataset):
    """Dataset of (query, chunk_path) pairs from JSONL."""

    def __init__(self, jsonl_path: str):
        self.pairs = []
        with open(jsonl_path) as f:
            for line in f:
                item = json.loads(line)
                self.pairs.append((item["query"], item["chunk_path"]))
        logger.info(f"Loaded {len(self.pairs)} pairs from {jsonl_path}")

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        return self.pairs[idx]
