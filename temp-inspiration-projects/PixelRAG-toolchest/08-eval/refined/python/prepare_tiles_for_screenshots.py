def prepare_tiles_for_screenshots(
    screenshot_dir: str, tiles_dir: str, tile_size: int = 512, overlap: int = 0
) -> dict[str, list[str]]:
    """Split all screenshots in a directory into tiles.

    Args:
        screenshot_dir: Directory containing full screenshots.
        tiles_dir: Directory to save tiles.
        tile_size: Size of each tile.
        overlap: Overlap between tiles.

    Returns:
        Dict mapping original image path to list of tile paths.
    """
    os.makedirs(tiles_dir, exist_ok=True)

    result = {}
    for filename in os.listdir(screenshot_dir):
        if not filename.endswith(".png"):
            continue

        image_path = os.path.join(screenshot_dir, filename)
        tile_paths = split_image_to_tiles(image_path, tiles_dir, tile_size, overlap)

        if tile_paths:
            result[image_path] = tile_paths
            logger.info(f"Split {filename} into {len(tile_paths)} tiles")

    logger.info(
        f"Total: {sum(len(v) for v in result.values())} tiles from {len(result)} images"
    )
    return result
