def _get_all_inat_image_paths(example: dict, tiles_dir: str) -> list[str]:
    """Get ALL iNaturalist query image paths for an example (not just the first)."""
    inat_ids = example.get("inat_image_ids", [])
    if not inat_ids:
        return []
    cache_dir = os.path.join(os.path.dirname(tiles_dir), "inat_images_multi")
    os.makedirs(cache_dir, exist_ok=True)
    example_id = example.get("id", "unknown")
    import shutil

    id_map = TiledQwen3VLEmbeddingRetriever._load_inat2021_mapping()
    paths = []
    for i, str_id in enumerate(inat_ids):
        local_path = os.path.join(cache_dir, f"{example_id}_{i}.jpg")
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            paths.append(local_path)
            continue
        try:
            img_id = int(str_id)
        except ValueError:
            continue
        file_name = id_map.get(img_id)
        if not file_name:
            continue
        src_path = os.path.join(_INAT2021_DATA_DIR, file_name)
        if os.path.exists(src_path) and os.path.getsize(src_path) > 0:
            shutil.copy2(src_path, local_path)
            paths.append(local_path)
    return paths
