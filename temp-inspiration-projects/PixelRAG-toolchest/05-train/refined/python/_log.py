def _log(msg: str):
    """Write log line directly to file descriptor (wandb-proof)."""
    global _log_fd
    if _log_fd is None:
        _log_fd = open(LOG_PATH, "w", buffering=1)  # line-buffered
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    _log_fd.write(f"{ts} {msg}\n")
    _log_fd.flush()
