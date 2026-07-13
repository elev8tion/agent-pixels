def _embed_tile_infos_with_engine(
    engine,
    gpu_id: int,
    tile_infos: list[TileInfo],
    batch_size: int,
    result_dir: str,
    embed_fn,
    prompt: str,
    io_workers: int = 8,
    compress_npz: bool = False,
    max_pixels: int | None = None,
    chunk_height: int | None = None,
    task_id: str | None = None,
) -> str:
    """Embed tile infos with a pre-initialized engine function + prompt.

    Uses a pipeline: background threads read files, hash, and decode only
    unique tiles while the main thread feeds decoded batches to the GPU.
    Duplicate tiles are hashed but never decoded.
    If chunk_height is set, tall tiles are split into chunks of that height.
    If max_pixels is set, images are resized in the I/O threads (overlaps GPU).
    """
    tile_hashes: list[tuple[TileInfo, str]] = []  # filled by producer
    unique_queue: queue.Queue = queue.Queue(maxsize=batch_size * 2)
    producer_error: list[Exception | None] = [None]

    resized_wide = [0]  # mutable counter for threads

    def _io_producer() -> None:
        """Read tiles, chunk tall images, hash chunks, skip decode for duplicates."""
        seen: set[str] = set()
        lock = threading.Lock()
        results_lock = threading.Lock()

        def _read_chunk_hash(ti):
            img_path = _image_path(ti)
            try:
                raw = Path(img_path).read_bytes()
                img = Image.open(io.BytesIO(raw)).convert("RGB")
            except Exception as e:
                logger.warning("Skipping unreadable image %s: %s", img_path, e)
                return []

            # Chunk tall images into strips (skip if already pre-chunked)
            if chunk_height is not None and not isinstance(ti, ChunkInfo):
                chunks = _chunk_image(img, chunk_height)
            else:
                chunks = [img]

            out = []
            for ci, chunk_img in enumerate(chunks):
                if max_pixels is not None:
                    chunk_img = _smart_resize_pil(chunk_img, max_pixels)
                cw, ch = chunk_img.size
                # Skip chunks with extreme aspect ratio (sglang rejects >200)
                if ch < 5 or (cw / max(ch, 1)) > 150:
                    logger.warning(
                        "Skipping bad chunk %s ci=%d size=%dx%d (aspect ratio %.1f)",
                        img_path,
                        ci,
                        cw,
                        ch,
                        cw / max(ch, 1),
                    )
                    continue
                if cw > _MAX_CHUNK_WIDTH:
                    chunk_img = _clamp_width_pil(chunk_img, _MAX_CHUNK_WIDTH)
                    cw, ch = chunk_img.size
                    resized_wide[0] += 1
                    logger.debug(
                        "Resized wide chunk %s ci=%d to %dx%d",
                        img_path,
                        ci,
                        cw,
                        ch,
                    )
                # Dedup key: use file path for pre-chunked files (avoids
                # expensive tobytes + MD5 on ~2.7MB raw pixels per chunk)
                if isinstance(ti, ChunkInfo):
                    h = img_path  # unique on disk, no hash needed
                else:
                    chunk_bytes = chunk_img.tobytes()
                    h = hashlib.md5(chunk_bytes).hexdigest()
                if len(chunks) > 1:
                    if isinstance(ti, ChunkInfo):
                        chunk_ti = ti._replace(
                            chunk_index=ci,
                            chunk_height=chunk_img.size[1],
                        )
                    else:
                        chunk_ti = ti._replace(
                            chunk_index=ci,
                            tile_height=chunk_img.size[1],
                        )
                else:
                    chunk_ti = ti
                with lock:
                    is_new = h not in seen
                    if is_new:
                        seen.add(h)
                out.append((chunk_ti, h, chunk_img if is_new else None))
            return out

        try:
            with ThreadPoolExecutor(max_workers=io_workers) as pool:
                for items in pool.map(_read_chunk_hash, tile_infos):
                    for chunk_ti, h, img in items:
                        with results_lock:
                            tile_hashes.append((chunk_ti, h))
                        if img is not None:
                            unique_queue.put((h, img))
        except Exception as exc:
            producer_error[0] = exc
        finally:
            unique_queue.put(None)  # sentinel

    t0 = time.time()
    producer = threading.Thread(target=_io_producer, daemon=True)
    producer.start()

    # Consume unique decoded tiles and embed in batches (overlaps with I/O)
    hash_to_embedding: dict[str, np.ndarray] = {}
    batch_h: list[str] = []
    batch_imgs: list = []
    unique_total = 0
    embedded = 0
    embed_time_total = 0.0
    queue_wait_total = 0.0
    n_batches = 0
    first_item_time = None
    consecutive_failures = 0
    _MAX_CONSECUTIVE_FAILURES = (
        3  # after 3 consecutive CUDA failures, abort this work item
    )
    gpu_dead = False

    while True:
        tq0 = time.time()
        item = unique_queue.get()
        queue_wait_total += time.time() - tq0
        if item is None:
            break
        if first_item_time is None:
            first_item_time = time.time() - t0
        h, img = item
        batch_h.append(h)
        batch_imgs.append(img)
        unique_total += 1

        if len(batch_h) >= batch_size:
            if gpu_dead:
                # Drain queue without embedding
                batch_h, batch_imgs = [], []
                continue
            try:
                te0 = time.time()
                embs = embed_fn(engine, prompt, batch_imgs)
                embed_time_total += time.time() - te0
                n_batches += 1
                consecutive_failures = 0
                for hh, emb in zip(batch_h, embs):
                    hash_to_embedding[hh] = emb
            except Exception as e:
                consecutive_failures += 1
                logger.error(
                    "GPU %d: embed failed at offset %d (%d/%d consecutive): %s",
                    gpu_id,
                    embedded,
                    consecutive_failures,
                    _MAX_CONSECUTIVE_FAILURES,
                    e,
                )
                if consecutive_failures >= _MAX_CONSECUTIVE_FAILURES:
                    logger.error(
                        "GPU %d: %d consecutive failures — marking GPU as dead",
                        gpu_id,
                        consecutive_failures,
                    )
                    gpu_dead = True
            embedded += len(batch_h)
            batch_h, batch_imgs = [], []

    # Final partial batch
    if batch_h and not gpu_dead:
        try:
            te0 = time.time()
            embs = embed_fn(engine, prompt, batch_imgs)
            embed_time_total += time.time() - te0
            n_batches += 1
            for hh, emb in zip(batch_h, embs):
                hash_to_embedding[hh] = emb
        except Exception as e:
            logger.error("GPU %d: embed failed on final batch: %s", gpu_id, e)
        embedded += len(batch_h)

    producer.join()
    pipeline_s = time.time() - t0

    if producer_error[0]:
        logger.error("GPU %d: I/O producer failed: %s", gpu_id, producer_error[0])

    deduped = len(tile_hashes) - unique_total
    100.0 * deduped / len(tile_hashes) if tile_hashes else 0.0
    n_resized = resized_wide[0]
    logger.info(
        "GPU %d: %d images, %d unique (%d deduped, %d resized>%d), embedded %d, pipeline %.2fs (%.1f chunks/s)"
        " | embed=%.2fs (%d batches) queue_wait=%.2fs first_item=%.3fs",
        gpu_id,
        len(tile_hashes),
        unique_total,
        deduped,
        n_resized,
        _MAX_CHUNK_WIDTH,
        embedded,
        pipeline_s,
        embedded / pipeline_s if pipeline_s > 0 else 0,
        embed_time_total,
        n_batches,
        queue_wait_total,
        first_item_time or 0,
    )

    if not hash_to_embedding:
        logger.warning("GPU %d: no embeddings produced", gpu_id)
        if gpu_dead:
            raise RuntimeError(
                f"GPU {gpu_id}: CUDA dead after {_MAX_CONSECUTIVE_FAILURES} consecutive failures"
            )
        return ""

    # Detect chunk mode from the type of items in tile_hashes
    is_chunk_mode = tile_hashes and isinstance(tile_hashes[0][0], ChunkInfo)

    # Phase 3: expand back to all tiles/chunks, reusing embeddings for duplicate hashes
    all_embeddings = []
    all_article_ids = []
    all_tile_indices = []
    all_chunk_indices = []
    all_page_heights = []
    all_viewport_widths = []
    all_tile_heights = []
    all_image_hashes = []
    all_tile_paths = []
    all_y_offsets = [] if is_chunk_mode else None

    for ti, h in tile_hashes:
        if h not in hash_to_embedding:
            continue  # embedding failed for this hash
        all_embeddings.append(hash_to_embedding[h])
        all_article_ids.append(ti.article_id)
        all_tile_indices.append(ti.tile_index)
        all_page_heights.append(ti.page_height)
        all_viewport_widths.append(ti.viewport_width)
        all_image_hashes.append(h)
        if is_chunk_mode:
            all_chunk_indices.append(ti.chunk_index)
            all_tile_heights.append(ti.chunk_height)
            all_tile_paths.append(ti.chunk_path)
            all_y_offsets.append(ti.y_offset)
        else:
            all_chunk_indices.append(ti.chunk_index)
            all_tile_heights.append(ti.tile_height)
            all_tile_paths.append(ti.tile_path)

    if not all_embeddings:
        logger.warning("GPU %d: no embeddings after expansion", gpu_id)
        return ""

    suffix = f"_{task_id}" if task_id else ""
    partial_path = os.path.join(result_dir, f"partial_gpu{gpu_id}{suffix}.npz")
    t_write0 = time.time()
    extra_arrays = {}
    if is_chunk_mode:
        extra_arrays["y_offsets"] = np.array(all_y_offsets, dtype=np.int32)
    save_npz(
        partial_path,
        compressed=compress_npz,
        embeddings=np.stack(all_embeddings),
        article_ids=np.array(all_article_ids, dtype=np.int64),
        tile_indices=np.array(all_tile_indices, dtype=np.int32),
        chunk_indices=np.array(all_chunk_indices, dtype=np.int32),
        page_heights=np.array(all_page_heights, dtype=np.int32),
        viewport_widths=np.array(all_viewport_widths, dtype=np.int32),
        tile_heights=np.array(all_tile_heights, dtype=np.int32),
        image_hashes=np.array(all_image_hashes, dtype="S32"),
        tile_paths=np.array(all_tile_paths, dtype="S512"),
        **extra_arrays,
    )
    write_s = time.time() - t_write0
    logger.info(
        "GPU %d: wrote %d embeddings (%d unique) to %s [pipeline %.2fs, write %.2fs]",
        gpu_id,
        len(all_embeddings),
        len(hash_to_embedding),
        partial_path,
        pipeline_s,
        write_s,
    )
    return partial_path
