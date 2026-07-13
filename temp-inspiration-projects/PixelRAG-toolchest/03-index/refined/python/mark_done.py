def mark_done(
        self,
        shard_id: int,
        completed: int = 0,
        failed: int = 0,
        skipped: int = 0,
        tiles: int = 0,
        expected: int = 0,
    ) -> None:
        """Mark shard as completed or partial.

        Compares actual output (completed + skipped) against *expected* to
        decide the final status.  If expected > 0 and actual < 90% of
        expected, the shard is marked ``partial`` so it can be reclaimed
        and resumed later.

        Args:
            shard_id: Shard ID to mark done.
            completed: Final number of completed articles.
            failed: Final number of failed articles.
            skipped: Final number of skipped articles.
            tiles: Final number of tile images produced.
            expected: Expected number of non-redirect articles in this shard.
                      Pass 0 to skip the completeness check (always "completed").
        """
        actual = completed + skipped
        if expected > 0 and actual < expected * 0.9:
            status = "partial"
        else:
            status = "completed"

        key = f"{self.prefix}/claims/{shard_id:03d}.json"
        claim_data = {
            "machine": self.machine_id,
            "hostname": self.hostname,
            "status": status,
            "claimed_at": self._claimed_at.pop(shard_id, time.time()),
            "heartbeat": time.time(),
            "completed_at": time.time(),
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "tiles": tiles,
            "expected": expected,
        }
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=json.dumps(claim_data))
        logger.info(
            "Shard %d marked %s (completed=%d, failed=%d, skipped=%d, tiles=%d, expected=%d)",
            shard_id,
            status,
            completed,
            failed,
            skipped,
            tiles,
            expected,
        )
