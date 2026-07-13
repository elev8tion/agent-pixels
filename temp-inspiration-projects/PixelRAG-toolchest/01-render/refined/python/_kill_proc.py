def _kill_proc(proc) -> None:
    """Best-effort kill + wait for a subprocess."""
    try:
        proc.send_signal(signal.SIGTERM)
    except Exception:
        pass
    try:
        proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
