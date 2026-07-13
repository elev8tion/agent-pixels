def read_tiles_and_hash_parallel(
    tile_infos: list[TileInfo],
    io_workers: int = 8,
) -> list[tuple[TileInfo, str, "Image.Image"]]:
    """Parallel tile read/hash/decode using a thread pool."""
    if io_workers <= 1 or len(tile_infos) <= 1:
        return read_tiles_and_hash(tile_infos)

    results: list[tuple[TileInfo, str, "Image.Image"]] = []
    with ThreadPoolExecutor(max_workers=io_workers) as pool:
        for item in pool.map(_read_hash_decode_one, tile_infos, chunksize=32):
            if item is not None:
                results.append(item)
    return results
