def _compute_tile_hashes(article_dir: str, tile_names: list[str]) -> dict[str, str]:
    """Compute MD5 hashes for all tile files."""
    hashes = {}
    for tn in tile_names:
        tp = os.path.join(article_dir, tn)
        if os.path.exists(tp):
            h = hashlib.md5()
            with open(tp, "rb") as f:
                for block in iter(lambda: f.read(65536), b""):
                    h.update(block)
            hashes[tn] = h.hexdigest()
    return hashes
