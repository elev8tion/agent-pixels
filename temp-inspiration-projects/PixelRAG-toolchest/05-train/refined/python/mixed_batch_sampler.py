class MixedBatchSampler(Sampler):
    """Yields batches with exact per-source counts from a ConcatDataset.

    Each source occupies a contiguous index range [start, start+length).
    Every batch draws exactly `count` samples from each source.
    Sources cycle (reshuffle) when exhausted.

    Args:
        source_ranges: list of (start_idx, dataset_length, count_per_batch)
        shuffle: shuffle indices within each source per epoch
        seed: base random seed
        rank/world_size: for distributed training (each rank gets disjoint batches)
    """

    def __init__(self, source_ranges, shuffle=True, seed=42, rank=0, world_size=1):
        self.source_ranges = source_ranges
        self.shuffle = shuffle
        self.seed = seed
        self.rank = rank
        self.world_size = world_size
        self.epoch = 0
        self._num_batches = min(
            length // count for _, length, count in source_ranges if count > 0
        )
        # In distributed mode, each rank gets a subset of batches
        self._num_batches = self._num_batches // world_size

    def set_epoch(self, epoch):
        self.epoch = epoch

    def __iter__(self):
        rng = torch.Generator()
        rng.manual_seed(self.seed + self.epoch)
        # Build shuffled index pools per source
        pools = []
        for start, length, count in self.source_ranges:
            if self.shuffle:
                perm = torch.randperm(length, generator=rng).tolist()
            else:
                perm = list(range(length))
            needed = (self._num_batches * self.world_size + 1) * count
            full = (perm * ((needed // length) + 1))[:needed]
            pools.append((start, full, count))
        # Yield batches for this rank
        total_batches = self._num_batches * self.world_size
        for b in range(total_batches):
            if b % self.world_size != self.rank:
                continue
            batch = []
            for start, pool, count in pools:
                offset = b * count
                batch.extend(start + pool[offset + i] for i in range(count))
            yield batch

    def __len__(self):
        return self._num_batches
