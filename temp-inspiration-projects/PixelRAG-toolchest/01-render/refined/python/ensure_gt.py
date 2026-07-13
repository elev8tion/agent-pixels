async def ensure_gt(
        self, n_articles: int = 200, seed: int = 42
    ) -> dict[str, list[Path]]:
        if self._gt is not None:
            return self._gt
        articles = self.prepare(n_articles, seed)
        gt_dir = self.output_dir / "ground_truth"
        self._gt = await generate_ground_truth(
            articles, self.chrome_path, gt_dir, seed, timeout_ms=self.gt_timeout_ms
        )
        ok, bad, examples = validate_gt(self._gt)
        total = ok + bad
        print(f"GT validation: {ok}/{total} OK, {bad} bad", flush=True)
        if examples:
            for ex in examples:
                print(f"  GT BAD: {ex}", flush=True)
        if bad > 0:
            pct = ok / total * 100 if total else 0
            if pct < CORRECT_THRESHOLD:
                raise RuntimeError(
                    f"GT itself is only {pct:.1f}% valid ({bad} bad tiles). "
                    f"Fix image loading or increase gt_timeout_ms."
                )
        return self._gt
