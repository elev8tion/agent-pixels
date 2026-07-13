def _get_all_query_image_paths(example: dict, tiles_dir: str) -> list[str]:
    """Get ALL query image paths for an EVQA example (all available images, not just the first).

    Falls back to the single ``query_image_path`` / ``_get_query_image_path_for_example``
    when the multi-image helpers return nothing (e.g. ``dataset_image_ids_parsed`` lives
    inside ``original_data`` rather than at top level).
    """
    ds = (example.get("dataset_name") or "").lower()
    if ds not in ("inaturalist", "landmarks"):
        od = example.get("original_data", {})
        if isinstance(od, str):
            import ast

            try:
                od = ast.literal_eval(od)
            except Exception:
                od = {}
        ds = (od.get("dataset_name") or "").lower()
    if ds == "inaturalist":
        paths = _get_all_inat_image_paths(example, tiles_dir)
    elif ds == "landmarks":
        paths = _get_all_landmark_image_paths(example, tiles_dir)
    else:
        paths = _get_all_inat_image_paths(example, tiles_dir)
    if not paths:
        single = example.get("query_image_path") or _get_query_image_path_for_example(
            example, tiles_dir, quiet=True
        )
        if single and os.path.exists(single):
            paths = [single]
    return paths
