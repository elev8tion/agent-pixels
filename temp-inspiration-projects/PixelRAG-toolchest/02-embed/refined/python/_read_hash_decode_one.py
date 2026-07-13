def _read_hash_decode_one(
    ti: TileInfo,
) -> tuple[TileInfo, str, "Image.Image"] | None:
    """Read one tile, compute hash, and decode into RGB image."""
    try:
        raw = Path(ti.tile_path).read_bytes()
        md5_hex = hashlib.md5(raw).hexdigest()
        # Decode from in-memory bytes to avoid a second filesystem read.
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        return (ti, md5_hex, img)
    except Exception as e:
        logger.warning("Failed to load %s: %s", ti.tile_path, e)
        return None
