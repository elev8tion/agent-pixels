def get_all_claims(self) -> list[dict]:
        """Read all claim files from S3.

        Returns:
            List of claim dicts, each augmented with 'shard_id' parsed from the key.
        """
        paginator = self.s3.get_paginator("list_objects_v2")
        claims = []
        for page in paginator.paginate(
            Bucket=self.bucket, Prefix=f"{self.prefix}/claims/"
        ):
            for obj in page.get("Contents", []):
                try:
                    data = self.s3.get_object(Bucket=self.bucket, Key=obj["Key"])
                    claim = json.loads(data["Body"].read())
                    # Parse shard ID from key: "kiwix/claims/042.json" -> 42
                    fname = obj["Key"].rsplit("/", 1)[-1]
                    claim["shard_id"] = int(fname.replace(".json", ""))
                    claims.append(claim)
                except Exception as e:
                    logger.warning("Failed to read claim %s: %s", obj["Key"], e)
        return claims
