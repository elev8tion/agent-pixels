def read_tiles_and_hash(
    tile_infos: list[TileInfo],
) -> list[tuple[TileInfo, str, "Image.Image"]]:
    """Read tile files, compute MD5 hashes, and load PIL images.

    Returns:
        List of (tile_info, md5_hex, pil_image) tuples for successfully loaded tiles.
    """
    results = []
    for ti in tile_infos:
        try:
            raw = Path(ti.tile_path).read_bytes()
            md5_hex = hashlib.md5(raw).hexdigest()
            img = Image.open(io.BytesIO(raw)).convert("RGB")
            results.append((ti, md5_hex, img))
        except Exception as e:
            logger.warning("Failed to load %s: %s", ti.tile_path, e)
    return results
