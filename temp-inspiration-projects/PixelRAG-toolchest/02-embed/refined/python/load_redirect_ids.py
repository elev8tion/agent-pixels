def load_redirect_ids(path: str) -> set[int]:
    """Load redirect article IDs from a .redirects.json file.

    The file is a dict mapping article index (str) to target path (str).
    We only need the keys (indices of redirect articles).

    Args:
        path: Path to the .redirects.json file.

    Returns:
        Set of article indices that are client-side redirects.
    """
    with open(path, "r") as f:
        redirects = json.load(f)
    ids = {int(k) for k in redirects}
    logger.info("Loaded %d redirect IDs from %s", len(ids), path)
    return ids
