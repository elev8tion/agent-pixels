def _get_query_image_path_for_example(
    example: dict, tiles_dir: str, quiet: bool = False
) -> str | None:
    """Get EVQA query image path. Dispatches by dataset_name: inaturalist | landmarks."""
    ds = (example.get("dataset_name") or "").lower()
    if ds == "inaturalist":
        return _get_inat_image_path_for_example(example, tiles_dir)
    if ds == "landmarks":
        return _get_landmark_image_path_for_example(example, tiles_dir, quiet=quiet)
    # Fallback: try inaturalist (backward compat when dataset_name missing)
    return _get_inat_image_path_for_example(example, tiles_dir)
