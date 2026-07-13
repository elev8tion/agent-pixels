def _dump_experiment(self, exp: dict):
        exp_dir = self.output_dir / "experiments"
        exp_dir.mkdir(parents=True, exist_ok=True)
        ts = exp["timestamp"].replace(":", "")
        name = exp["config"]["strategy_name"].replace(" ", "_").replace("/", "-")
        path = exp_dir / f"{ts}_{name}.json"
        path.write_text(json.dumps(exp, indent=2, default=str))
        print(f"Experiment saved: {path}", flush=True)
