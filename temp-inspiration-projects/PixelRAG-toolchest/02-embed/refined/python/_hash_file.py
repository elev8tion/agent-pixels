def _hash_file(path: str) -> str:
    """Compute MD5 hex digest of a file. Returns empty string on error."""
    try:
        return hashlib.md5(Path(path).read_bytes()).hexdigest()
    except OSError:
        return ""
