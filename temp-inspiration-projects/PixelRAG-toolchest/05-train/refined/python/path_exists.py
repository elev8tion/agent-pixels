def path_exists(path: str, cache: dict[str, bool], lock: threading.Lock) -> bool:
    with lock:
        cached = cache.get(path)
    if cached is not None:
        return cached
    exists = Path(path).exists()
    with lock:
        cache[path] = exists
    return exists
