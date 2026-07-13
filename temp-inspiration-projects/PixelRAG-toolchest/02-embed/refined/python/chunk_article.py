def chunk_article(article_dir: str, dry_run: bool = False, force: bool = False) -> dict:
    """Chunk all tiles in one article directory.

    Args:
        article_dir: Path to *.png.tiles/ directory.
        dry_run: If True, compute chunks but don't write files.
        force: If True, rechunk even if chunks.json exists (compare tile hashes).

    Returns:
        dict with chunking results, or None if up-to-date / skipped.
    """
    tiles_json = os.path.join(article_dir, "tiles.json")
    chunks_json = os.path.join(article_dir, "chunks.json")

    if not os.path.exists(tiles_json):
        return None

    with open(tiles_json) as f:
        raw = f.read().strip()
    if not raw:
        return None
    meta = json.loads(raw)

    tile_names = meta.get("tiles", [])
    if not tile_names:
        return None

    # Compute tile hashes (stored in manifest for future change detection)
    tile_hashes = _compute_tile_hashes(article_dir, tile_names)

    # If no tiles exist on disk, skip — never delete existing chunks without tiles to rechunk
    if not tile_hashes:
        return None

    if os.path.exists(chunks_json):
        try:
            with open(chunks_json) as f:
                old_manifest = json.load(f)
        except (json.JSONDecodeError, KeyError):
            old_manifest = None

        # Always verify chunk files actually exist on disk
        chunks_ok = old_manifest is not None and all(
            os.path.exists(os.path.join(article_dir, c["file"]))
            for c in old_manifest.get("chunks", [])
        )

        if chunks_ok:
            if not force:
                return None  # chunks exist, not forced, skip
            # Force: also check tile hashes
            old_hashes = old_manifest.get("tile_hashes", {})
            if old_hashes and old_hashes == tile_hashes:
                return None  # tiles unchanged and chunks exist, skip

        # Hashes differ or missing — delete old chunk files before rechunking
        if not dry_run:
            for f in os.listdir(article_dir):
                if f.startswith("chunk_") and f.endswith((".png", ".jpg", ".jpeg")):
                    os.unlink(os.path.join(article_dir, f))

    page_height = meta.get("page_height", 0)
    viewport_width = meta.get("viewport_width", 875)
    tile_height = meta.get("tile_height", 8192)

    chunks_info = []  # list of {tile, chunk_index, file, y_offset, height}
    files_written = 0

    for tile_name in tile_names:
        tile_path = os.path.join(article_dir, tile_name)
        if not os.path.exists(tile_path):
            continue

        try:
            img = Image.open(tile_path)
            w, h = img.size
        except Exception as e:
            logger.warning("Skipping corrupt tile %s: %s", tile_path, e)
            continue
        # Handle both .png and .jpg tile files
        tile_base = tile_name.replace("tile_", "")
        for ext in (".png", ".jpg", ".jpeg"):
            tile_base = tile_base.replace(ext, "")
        tile_idx = int(tile_base)

        # Fast path: web tiles (<= viewport_width) that fit one strip are copied
        # verbatim — byte-identical to the pre-2D-tiling behavior.
        if w <= viewport_width and h <= CHUNK_HEIGHT:
            chunk_name = f"chunk_{tile_idx:04d}_00.png"
            chunk_path = os.path.join(article_dir, chunk_name)
            if not dry_run:
                shutil.copy2(tile_path, chunk_path)
                files_written += 1
            chunks_info.append(
                {
                    "tile": tile_name,
                    "tile_index": tile_idx,
                    "chunk_index": 0,
                    "file": chunk_name,
                    "x_offset": 0,
                    "y_offset": 0,
                    "height": h,
                    "width": w,
                }
            )
            continue

        # 2D grid: CHUNK_HEIGHT-tall row strips x viewport_width-wide columns.
        # Columns are a full viewport_width each (the model's native width) with
        # the remainder in the last column — not evened out — so most content
        # lands at the in-distribution width the index was built on. chunk_index
        # is a flat row-major counter, so single-column tiles keep the same
        # 0, 1, 2, ... order (and identical crops) as before.
        chunk_idx = 0
        y = 0
        while y < h:
            ch = min(CHUNK_HEIGHT, h - y)
            # Discard tiny height tail (< 28px = one Qwen3-VL patch)
            if ch < MIN_CHUNK_HEIGHT:
                break

            x = 0
            while x < w:
                cw = min(viewport_width, w - x)
                if cw < MIN_CHUNK_HEIGHT:  # discard tiny right-edge sliver
                    break

                chunk_name = f"chunk_{tile_idx:04d}_{chunk_idx:02d}.png"
                chunk_path = os.path.join(article_dir, chunk_name)
                if not dry_run:
                    img.crop((x, y, x + cw, y + ch)).save(chunk_path, format="PNG")
                    files_written += 1

                chunks_info.append(
                    {
                        "tile": tile_name,
                        "tile_index": tile_idx,
                        "chunk_index": chunk_idx,
                        "file": chunk_name,
                        "x_offset": x,
                        "y_offset": y,
                        "height": ch,
                        "width": cw,
                    }
                )
                chunk_idx += 1
                x += cw

            y += ch

        img.close()

    if not chunks_info:
        return None

    # Write chunks.json
    manifest = {
        "page_height": page_height,
        "viewport_width": viewport_width,
        "tile_height": tile_height,
        "chunk_height": CHUNK_HEIGHT,
        "num_tiles": len(tile_names),
        "num_chunks": len(chunks_info),
        "tile_hashes": tile_hashes,
        "chunks": chunks_info,
    }

    if not dry_run:
        with open(chunks_json, "w") as f:
            json.dump(manifest, f)

    return {
        "article_dir": article_dir,
        "num_tiles": len(tile_names),
        "num_chunks": len(chunks_info),
        "files_written": files_written,
    }
