def debug_trace(enabled, message):
    """Emit a per-rank debug line when tracing distributed hangs."""
    if not enabled:
        return
    rank = dist.get_rank() if dist.is_initialized() else 0
    logger.info(f"[debug rank={rank}] {message}")
