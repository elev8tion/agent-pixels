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
