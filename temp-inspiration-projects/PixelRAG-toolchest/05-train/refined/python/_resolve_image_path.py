def _resolve_image_path(ex: dict, images_root: str) -> str:
    """chunk_path is relative to the dataset root (e.g. images/shard_000/...).
    images_root is the directory that contains the `images/` subtree (compressed or original)."""
    rel = ex["chunk_path"]
    if os.path.isabs(rel):
        return rel
    return os.path.join(images_root, rel)
