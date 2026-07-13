def get_status(self) -> dict:
        """Read all claims from S3 and return global status.

        Returns:
            Dict with keys: total_shards, completed, in_progress, stale,
            unclaimed, articles_done, machines, claims.
        """
        claims = self.get_all_claims()
        now = time.time()

        completed = sum(1 for c in claims if c["status"] == "completed")
        in_progress = sum(1 for c in claims if c["status"] == "in_progress")
        stale = sum(
            1
            for c in claims
            if c["status"] == "in_progress"
            and now - c.get("heartbeat", 0) > self.stale_timeout
        )
        total = self._manifest["num_shards"] if self._manifest else "?"
        unclaimed = (total - len(claims)) if isinstance(total, int) else "?"

        return {
            "total_shards": total,
            "completed": completed,
            "in_progress": in_progress - stale,
            "stale": stale,
            "unclaimed": unclaimed,
            "articles_done": sum(
                c.get("completed", 0) + c.get("failed", 0) + c.get("skipped", 0)
                for c in claims
            ),
            "machines": list(
                set(c["machine"] for c in claims if c["status"] == "in_progress")
            ),
            "claims": claims,
        }
