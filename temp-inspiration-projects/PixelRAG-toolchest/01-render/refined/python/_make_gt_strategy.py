def _make_gt_strategy(chrome_path: str, timeout_ms: int):
    """GT uses the most conservative strategy: 1 worker, PNG, long timeout.

    Uses port 9222 to avoid TIME_WAIT conflicts with test strategies (9300+).
    """
    s = CDPSequentialStrategy(
        chrome_path=chrome_path, n_workers=1, fmt="png", from_surface=True
    )
    s._base_port = 9222
    return s
