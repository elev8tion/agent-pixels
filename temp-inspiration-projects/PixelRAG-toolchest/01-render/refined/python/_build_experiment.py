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
