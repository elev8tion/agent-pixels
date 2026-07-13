def _parse_new_jsonl(results_file: Path, lines_before: int, state: dict, cycle: dict):
    """Parse newly appended lines from a JSONL results file into state/cycle."""
    if not results_file.exists():
        return
    with open(results_file) as f:
        for i, line in enumerate(f):
            if i < lines_before:
                continue
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            issues = rec.get("issues", [])
            # Don't count API_ERROR as quality failures (transient network issues)
            if issues == ["API_ERROR"]:
                continue
            state["tiles_checked"] += 1
            cycle["tiles_checked"] += 1
            if not rec.get("pass", False):
                state["tiles_failed"] += 1
                cycle["tiles_failed"] += 1
                for issue in issues:
                    state["issues"][issue] += 1
                    cycle["issues"][issue] += 1
