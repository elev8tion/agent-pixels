def resolve_gpu_ids(gpu_ids_arg: str) -> list[int]:
    """Resolve GPU IDs from CLI arg.

    Supports:
    - "all" / "auto": use all visible GPUs
    - comma-separated IDs, e.g. "0,1,2,3"
    """
    value = gpu_ids_arg.strip().lower()
    if value in {"all", "auto"}:
        visible = os.environ.get("CUDA_VISIBLE_DEVICES", "").strip()
        if visible:
            parts = [p.strip() for p in visible.split(",") if p.strip()]
            if parts:
                # Under CUDA_VISIBLE_DEVICES, local IDs are 0..N-1.
                return list(range(len(parts)))
        try:
            out = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=index", "--format=csv,noheader"],
                text=True,
            )
            lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
            if lines:
                return list(range(len(lines)))
        except Exception:
            logger.warning(
                "Failed to detect GPUs via nvidia-smi; falling back to GPU 0"
            )
        return [0]

    return [int(g.strip()) for g in gpu_ids_arg.split(",") if g.strip()]
