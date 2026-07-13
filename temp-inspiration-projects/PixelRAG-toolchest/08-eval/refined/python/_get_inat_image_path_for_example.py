def _get_inat_image_path_for_example(example: dict, tiles_dir: str) -> str | None:
    """Get iNaturalist 2021 query image path. dataset_name must be 'inaturalist'."""
    inat_ids = example.get("inat_image_ids", [])
    if not inat_ids:
        return None
    cache_dir = os.path.join(os.path.dirname(tiles_dir), "inat_images")
    os.makedirs(cache_dir, exist_ok=True)
    example_id = example.get("id", "unknown")
    local_path = os.path.join(cache_dir, f"{example_id}.jpg")
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return local_path
    import shutil

    id_map = TiledQwen3VLEmbeddingRetriever._load_inat2021_mapping()
    for str_id in inat_ids:
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
            return local_path
    logger.warning(f"Failed to find iNaturalist image for {example_id}")
    return None
