def _run_validate_tiles(
    output_dir: str,
    sample: int,
    shard_ids: list[int],
    state: dict,
    model: str | None = None,
) -> dict:
    """Run validate_tiles.py locally on given shards and parse JSONL results."""
    cycle = {"tiles_checked": 0, "tiles_failed": 0, "issues": collections.Counter()}
    if not shard_ids:
        return cycle

    results_file = state["results_file"]
    # --shard uses nargs="+", so place it before --concurrency which
    # terminates the greedy list (otherwise "local" gets consumed as a shard).
    cmd = [
        sys.executable,
        _VALIDATE_SCRIPT,
        "--sample",
        str(sample),
        "--shard",
        *(str(s) for s in shard_ids),
        "--concurrency",
        "10",
        "--seed",
        str(int(time.time())),
        "--resume",
        str(results_file),
    ]
    if model:
        cmd += ["--model", model]
    cmd += ["local", output_dir]

    try:
        lines_before = _count_lines(results_file)
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300, env=_validate_env()
        )
        if proc.returncode not in (0, 1):
            return cycle
        _parse_new_jsonl(results_file, lines_before, state, cycle)
    except (subprocess.TimeoutExpired, Exception):
        pass

    return cycle
