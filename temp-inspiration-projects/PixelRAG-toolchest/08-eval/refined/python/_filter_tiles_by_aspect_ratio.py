def _filter_tiles_by_aspect_ratio(
    tile_paths: list[str], max_aspect_ratio: float = 100.0
) -> list[str]:
    """Filter out tiles with extreme aspect ratios.

    Args:
        tile_paths: List of tile image paths.
        max_aspect_ratio: Maximum allowed aspect ratio (default 100, ColQwen requires < 200).

    Returns:
        Filtered list of tile paths.
    """
    from PIL import Image

    filtered = []
    for tile_path in tile_paths:
        try:
            with Image.open(tile_path) as img:
                w, h = img.size
                if w > 0 and h > 0:
                    aspect_ratio = max(w / h, h / w)
                    if aspect_ratio <= max_aspect_ratio:
                        filtered.append(tile_path)
                    else:
                        logger.warning(
                            f"Skipping tile with extreme aspect ratio {aspect_ratio:.2f}: {tile_path}"
                        )
        except Exception as e:
            logger.warning(f"Failed to check tile {tile_path}: {e}")

    return filtered
