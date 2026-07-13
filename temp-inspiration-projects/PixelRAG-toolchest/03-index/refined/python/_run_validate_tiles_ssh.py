def _run_validate_tiles_ssh(
    ssh_spec: str,
    sample: int,
    shard_ids: list[int],
    state: dict,
    model: str | None = None,
) -> dict:
    """SSH to a remote machine, run validate_tiles.py on given shards, scp results back.

    ssh_spec format: ``user@host:/project/dir`` (project dir contains
    ``output_coordinated/`` and ``validation/``).
    """
    cycle = {"tiles_checked": 0, "tiles_failed": 0, "issues": collections.Counter()}
    if not shard_ids:
        return cycle

    ssh_host, project_dir = _parse_ssh_spec(ssh_spec)
    local_results = state["results_file_ssh"][ssh_spec]

    remote_output = f"{project_dir}/output_coordinated"
    remote_python = f"{project_dir}/validation/.venv/bin/python"
    remote_script = f"{project_dir}/validation/validate_tiles.py"
    remote_results = f"{project_dir}/validation/results/monitor_validation.jsonl"
    remote_results_dir = f"{project_dir}/validation/results"

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    seed = str(int(time.time()))
    shard_args = " ".join(str(s) for s in shard_ids)

    model_arg = f" --model {model}" if model else ""
    remote_cmd = (
        f"mkdir -p {remote_results_dir} && rm -f {remote_results} && "
        f"GOOGLE_API_KEY={api_key} {remote_python} {remote_script}"
        f" --sample {sample} --concurrency 10 --seed {seed}"
        f"{model_arg}"
        f" --shard {shard_args}"
        f" local {remote_output}"
    )

    ssh_cmd = [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "ConnectTimeout=10",
        ssh_host,
        remote_cmd,
    ]

    try:
        proc = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=300)
        if proc.returncode not in (0, 1):
            return cycle

        # SCP the remote results file back
        lines_before = _count_lines(local_results)
        scp_cmd = [
            "scp",
            "-o",
            "StrictHostKeyChecking=no",
            "-q",
            f"{ssh_host}:{remote_results}",
            str(local_results),
        ]
        subprocess.run(scp_cmd, capture_output=True, timeout=30)
        _parse_new_jsonl(local_results, lines_before, state, cycle)
    except (subprocess.TimeoutExpired, Exception):
        pass

    return cycle
