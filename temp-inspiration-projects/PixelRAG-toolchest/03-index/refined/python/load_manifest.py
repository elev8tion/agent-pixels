def load_manifest(self) -> dict:
        """Load shard manifest from S3.

        Returns:
            Manifest dict with keys: total, num_shards, shards.
        """
        key = f"{self.prefix}/manifest.json"
        logger.info("Loading manifest from s3://%s/%s", self.bucket, key)
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        self._manifest = json.loads(obj["Body"].read())
        logger.info(
            "Loaded manifest: %d shards, %d total articles",
            self._manifest["num_shards"],
            self._manifest["total"],
        )
        return self._manifest
