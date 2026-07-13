def mark_partial(
        self,
        shard_id: int,
        completed: int = 0,
        failed: int = 0,
        skipped: int = 0,
        tiles: int = 0,
        error: str = "",
    ) -> None:
        """Explicitly mark a shard as partial after an error.

        Unlike mark_done, this always sets status to ``partial`` regardless
        of counts.  The shard stays reclaimable so another worker (or the
        same worker on restart) can resume from where it left off.
        """
        key = f"{self.prefix}/claims/{shard_id:03d}.json"
        claim_data = {
            "machine": self.machine_id,
            "hostname": self.hostname,
            "status": "partial",
            "claimed_at": self._claimed_at.pop(shard_id, time.time()),
            "heartbeat": time.time(),
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "tiles": tiles,
            "error": error,
        }
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=json.dumps(claim_data))
        logger.info(
            "Shard %d marked partial (completed=%d, tiles=%d, error=%s)",
            shard_id,
            completed,
            tiles,
            error[:120],
        )
