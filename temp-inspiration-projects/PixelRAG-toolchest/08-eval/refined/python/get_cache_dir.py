def get_cache_dir() -> Path:
    """Get the cache directory for downloaded datasets."""
    cache_dir = Path.home() / ".cache" / "dr_agent" / "datasets"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
