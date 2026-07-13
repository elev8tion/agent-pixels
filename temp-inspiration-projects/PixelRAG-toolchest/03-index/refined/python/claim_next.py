def claim_next(self) -> dict | None:
        """Claim the next available shard.

        Iterates through all shards and claims the first one that is either
        unclaimed or stale (heartbeat older than stale_timeout).

        Uses S3 conditional writes (IfNoneMatch / IfMatch) to prevent race
        conditions where two machines claim the same shard simultaneously.

        Returns:
            Shard dict with keys {id, start, end, count}, or None if all done.
        """
        if not self._manifest:
            self.load_manifest()

        for shard in self._manifest["shards"]:
            key = f"{self.prefix}/claims/{shard['id']:03d}.json"

            # Check if already claimed
            etag = None  # Track ETag for conditional reclaim
            try:
                obj = self.s3.get_object(Bucket=self.bucket, Key=key)
                claim = json.loads(obj["Body"].read())
                if claim["status"] == "completed":
                    continue
                if claim["status"] == "partial":
                    # Partial shard — only reclaim on the SAME host that
                    # originally ran it (that host still has the local data
                    # on NVMe, so it can resume efficiently).
                    claim_host = claim.get("hostname", "")
                    if claim_host and claim_host != self.hostname:
                        continue  # Leave it for the original host
                    etag = obj.get("ETag")
                    logger.info(
                        "Reclaiming partial shard %d (completed=%d, host=%s)",
                        shard["id"],
                        claim.get("completed", 0),
                        claim_host or claim.get("machine", "?"),
                    )
                elif claim["status"] == "in_progress":
                    age = time.time() - claim.get("heartbeat", 0)
                    if age < self.stale_timeout:
                        continue  # Still active
                    # Stale — prefer same host (local NVMe data).
                    # Only allow cross-host reclaim after 2x stale_timeout
                    # (original host is probably permanently down).
                    claim_host = claim.get("hostname", "")
                    if claim_host and claim_host != self.hostname:
                        if age < self.stale_timeout * 2:
                            continue  # Give the original host more time
                    etag = obj.get("ETag")
                    logger.info(
                        "Reclaiming stale shard %d (last heartbeat %.0fs ago, host=%s)",
                        shard["id"],
                        age,
                        claim_host or claim.get("machine", "?"),
                    )
            except ClientError as e:
                if e.response["Error"]["Code"] != "NoSuchKey":
                    raise
                # Key doesn't exist -> unclaimed, will use IfNoneMatch

            # Try to claim with conditional write to prevent races
            claim_data = {
                "machine": self.machine_id,
                "hostname": self.hostname,
                "status": "in_progress",
                "claimed_at": time.time(),
                "heartbeat": time.time(),
                "completed": 0,
                "failed": 0,
                "skipped": 0,
            }
            try:
                put_kwargs = {
                    "Bucket": self.bucket,
                    "Key": key,
                    "Body": json.dumps(claim_data),
                }
                if etag is not None:
                    # Reclaiming stale shard: only succeed if nobody else
                    # reclaimed it since our GET (ETag still matches).
                    put_kwargs["IfMatch"] = etag
                else:
                    # New claim: only succeed if key doesn't exist yet.
                    put_kwargs["IfNoneMatch"] = "*"

                self.s3.put_object(**put_kwargs)
                self._claimed_at[shard["id"]] = claim_data["claimed_at"]
                logger.info(
                    "Claimed shard %d (articles %d-%d)",
                    shard["id"],
                    shard["start"],
                    shard["end"],
                )
                return shard
            except ClientError as e:
                code = e.response["Error"]["Code"]
                if code in (
                    "PreconditionFailed",
                    "ConditionalCheckFailed",
                    "ConditionalRequestConflict",
                ):
                    # Another machine claimed it first — try next shard
                    logger.debug(
                        "Lost claim race for shard %d, trying next",
                        shard["id"],
                    )
                    continue
                raise
            except Exception:
                continue

        return None  # All shards claimed or completed
