def heartbeat(
        self,
        shard_id: int,
        completed: int = 0,
        failed: int = 0,
        skipped: int = 0,
        tiles: int = 0,
        **extra,
    ) -> None:
        """Update claim with current progress.

        Args:
            shard_id: Shard ID to update.
            completed: Number of completed articles.
            failed: Number of failed articles.
            skipped: Number of skipped articles.
            tiles: Number of tile images produced.
            **extra: Additional fields merged into the claim JSON. Known fields:
                disk_free_gb (float) — free disk space on the worker's output volume.
                s3_sync (bool) — whether this worker syncs output to S3.
                in_flight (list[str]) — article IDs currently being processed.
                recent_errors (list[str]) — last N error messages.
                fail_rate (float) — failed / total articles ratio.
        """
        key = f"{self.prefix}/claims/{shard_id:03d}.json"
        claim_data = {
            "machine": self.machine_id,
            "hostname": self.hostname,
            "status": "in_progress",
            "claimed_at": self._claimed_at.get(shard_id, time.time()),
            "heartbeat": time.time(),
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "tiles": tiles,
            **extra,
        }
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=json.dumps(claim_data))
