@atexit.register
def _cleanup_sources() -> None:
    for src in list(_active_sources):
        try:
            src.close()
        except Exception:
            pass
