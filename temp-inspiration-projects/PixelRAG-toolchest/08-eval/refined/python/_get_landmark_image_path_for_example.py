def _get_landmark_image_path_for_example(
    example: dict, tiles_dir: str, quiet: bool = False
) -> str | None:
    """Get Google Landmarks v2 query image path. dataset_name must be 'landmarks'.

    GLDv2 stores images as {split}/{a}/{b}/{c}/{id}.jpg (a,b,c = first 3 chars of id).
    Searches train, index, test in order.
    """
    ids = example.get("dataset_image_ids_parsed", [])
    if not ids:
        return None
    cache_dir = os.path.join(os.path.dirname(tiles_dir), "landmark_images")
    os.makedirs(cache_dir, exist_ok=True)
    example_id = example.get("id", "unknown")
    local_path = os.path.join(cache_dir, f"{example_id}.jpg")
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return local_path
    import shutil

    data_dir = _LANDMARK_V2_DATA_DIR
    for img_id in ids:
        if len(img_id) < 3:
            continue
        # GLDv2 path: {split}/{a}/{b}/{c}/{id}.jpg
        subpath = f"{img_id[0]}/{img_id[1]}/{img_id[2]}/{img_id}.jpg"
        for split in ("train", "index", "test"):
            src_path = os.path.join(data_dir, split, subpath)
            if os.path.exists(src_path) and os.path.getsize(src_path) > 0:
                shutil.copy2(src_path, local_path)
                return local_path
    # Fallback: download from train.csv URL (requires data/landmark_v2/train.csv)
    # Try each img_id in order; first URL may be 404, others might work
    for img_id in ids:
        if _try_download_landmark_from_url(example_id, img_id, local_path):
            return local_path
    if not quiet:
        logger.warning(
            f"Failed to find Landmark image for {example_id} (data in {data_dir}?)"
        )
    return None
