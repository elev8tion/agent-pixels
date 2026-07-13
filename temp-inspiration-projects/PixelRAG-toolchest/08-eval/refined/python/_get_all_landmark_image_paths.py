def _get_all_landmark_image_paths(example: dict, tiles_dir: str) -> list[str]:
    """Get ALL Google Landmarks query image paths for an example (not just the first)."""
    ids = example.get("dataset_image_ids_parsed", [])
    if not ids:
        return []
    cache_dir = os.path.join(os.path.dirname(tiles_dir), "landmark_images_multi")
    os.makedirs(cache_dir, exist_ok=True)
    example_id = example.get("id", "unknown")
    import shutil

    data_dir = _LANDMARK_V2_DATA_DIR
    paths = []
    for i, img_id in enumerate(ids):
        local_path = os.path.join(cache_dir, f"{example_id}_{i}.jpg")
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            paths.append(local_path)
            continue
        if len(img_id) < 3:
            continue
        subpath = f"{img_id[0]}/{img_id[1]}/{img_id[2]}/{img_id}.jpg"
        found = False
        for split in ("train", "index", "test"):
            src_path = os.path.join(data_dir, split, subpath)
            if os.path.exists(src_path) and os.path.getsize(src_path) > 0:
                shutil.copy2(src_path, local_path)
                paths.append(local_path)
                found = True
                break
        if not found:
            if _download_landmark_image_by_id(img_id, local_path):
                paths.append(local_path)
    return paths
