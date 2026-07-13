def download_file(url: str, cache_name: str) -> Path:
    """Download file from URL to cache directory if not already cached."""
    cache_path = get_cache_dir() / cache_name
    if not cache_path.exists():
        urllib.request.urlretrieve(url, cache_path)
    return cache_path
