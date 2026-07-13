def split_image_to_tiles(
    image_path: str,
    output_dir: str,
    tile_size: int | tuple[int, int] = 512,
    overlap: int = 0,
) -> list[str]:
    """Split an image into fixed-size tiles.

    Args:
        image_path: Path to the source image.
        output_dir: Directory to save tiles.
        tile_size: Size of each tile. Can be int (square) or tuple (width, height).
        overlap: Overlap between tiles in pixels.

    Returns:
        List of tile file paths.
    """
    from PIL import Image
    import glob

    if not os.path.exists(image_path):
        return []

    os.makedirs(output_dir, exist_ok=True)

    # Get base name without extension
    base_name = os.path.splitext(os.path.basename(image_path))[0]

    # Check if tiles already exist for this image
    existing_tiles = sorted(
        glob.glob(os.path.join(output_dir, f"{base_name}_tile_*.png"))
    )
    if existing_tiles:
        # Tiles already exist, return them
        return existing_tiles

    # Support both square and rectangular tiles
    if isinstance(tile_size, tuple):
        tile_w, tile_h = tile_size
    else:
        tile_w = tile_h = tile_size

    try:
        Image.MAX_IMAGE_PIXELS = 300_000_000
        img = Image.open(image_path)
        width, height = img.size

        tile_paths = []
        step_x = tile_w - overlap
        step_y = tile_h - overlap

        row = 0
        y = 0
        while y < height:
            col = 0
            x = 0
            while x < width:
                # Calculate tile boundaries
                x2 = min(x + tile_w, width)
                y2 = min(y + tile_h, height)

                # Calculate tile dimensions
                tile_width = x2 - x
                tile_height = y2 - y

                # Skip tiles with extreme aspect ratios (> 10:1)
                # This prevents issues with ColQwen which requires aspect ratio < 200
                if tile_width > 0 and tile_height > 0:
                    aspect_ratio = max(
                        tile_width / tile_height, tile_height / tile_width
                    )
                    if aspect_ratio > 10:
                        col += 1
                        x += step_x
                        if x >= width:
                            break
                        continue

                # Crop tile
                tile = img.crop((x, y, x2, y2))

                # Save tile
                tile_filename = f"{base_name}_tile_{row}_{col}.png"
                tile_path = os.path.join(output_dir, tile_filename)
                tile.save(tile_path)
                tile_paths.append(tile_path)

                col += 1
                x += step_x
                if x >= width:
                    break

            row += 1
            y += step_y
            if y >= height:
                break

        img.close()
        return tile_paths

    except Exception as e:
        logger.warning(f"Failed to split image {image_path}: {e}")
        return []
