def _load_landmark_url_map() -> dict[str, str]:
    """Load GLDv2 train.csv: img_id -> url. Cached after first call."""
    global _landmark_url_map_cache
    if _landmark_url_map_cache is not None:
        return _landmark_url_map_cache
    import csv

    train_csv = os.path.join(_LANDMARK_V2_DATA_DIR, "train.csv")
    if not os.path.exists(train_csv):
        _landmark_url_map_cache = {}
        return _landmark_url_map_cache
    url_map = {}
    with open(train_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            img_id = row.get("id", "").strip()
            url = row.get("url", "").strip()
            if img_id and url:
                url_map[img_id] = url
    _landmark_url_map_cache = url_map
    logger.info(f"Loaded landmark URL map: {len(url_map)} entries")
    return url_map
