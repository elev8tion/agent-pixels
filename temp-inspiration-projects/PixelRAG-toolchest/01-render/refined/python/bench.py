class Bench:
    """Benchmark harness. Measures throughput/latency and verifies correctness.

    Usage:
        bench = Bench(zim_path="...", chrome_path="...", output_dir="./results")
        result = await bench.run(strategy, articles=200, seed=42)
    """

    def __init__(
        self,
        zim_path: str,
        chrome_path: str,
        output_dir: str = "./bench_results",
        kiwix_url: str | None = None,
        gt_timeout_ms: int = 5000,
    ):
        self.zim_path = zim_path
        self.chrome_path = chrome_path
        self.output_dir = Path(output_dir)
        self.kiwix_url = kiwix_url
        self.gt_timeout_ms = gt_timeout_ms
        self._articles: list[dict] | None = None
        self._gt: dict[str, list[Path]] | None = None

    def prepare(self, n_articles: int = 200, seed: int = 42) -> list[dict]:
        if self._articles is None:
            self._articles = prepare_articles(
                self.zim_path, n_articles, seed, kiwix_url=self.kiwix_url
            )
        return self._articles

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

    def _build_experiment(
        self, strategy, result: dict, n_articles: int, seed: int
    ) -> dict:
        config = {
            "strategy_class": type(strategy).__name__,
            "strategy_name": strategy.name,
            "n_workers": getattr(strategy, "n_workers", None),
            "fmt": strategy.fmt,
            "launcher": getattr(strategy, "launcher", None),
            "from_surface": getattr(strategy, "from_surface", None),
            "chrome_path": getattr(strategy, "chrome_path", None),
            "n_articles": n_articles,
            "seed": seed,
            "zim_path": self.zim_path,
            "kiwix_url": self.kiwix_url,
            "gt_timeout_ms": self.gt_timeout_ms,
        }
        return {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "config": config,
            "results": {k: v for k, v in result.items() if k != "bad_examples"},
            "bad_examples": result.get("bad_examples", []),
        }

    def _dump_experiment(self, exp: dict):
        exp_dir = self.output_dir / "experiments"
        exp_dir.mkdir(parents=True, exist_ok=True)
        ts = exp["timestamp"].replace(":", "")
        name = exp["config"]["strategy_name"].replace(" ", "_").replace("/", "-")
        path = exp_dir / f"{ts}_{name}.json"
        path.write_text(json.dumps(exp, indent=2, default=str))
        print(f"Experiment saved: {path}", flush=True)
