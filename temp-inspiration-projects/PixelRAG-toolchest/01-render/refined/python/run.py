async def run(self, strategy, n_articles: int = 200, seed: int = 42) -> dict:
        articles = self.prepare(n_articles, seed)
        gt = await self.ensure_gt(n_articles, seed)
        result = await run_and_verify(strategy, articles, gt)

        exp = self._build_experiment(strategy, result, n_articles, seed)
        try:
            self._dump_experiment(exp)
        except Exception as e:
            print(f"Warning: failed to save experiment: {e}", flush=True)
        return result
