async def evaluate_one(
    idx: int,
    row: dict,
    llm_client: LLMClient,
    mode: str,
    args: argparse.Namespace,
    semaphore: asyncio.Semaphore,
    # Pre-computed retrieval results (populated during batch retrieval phase)
    pixel_items: list[dict] | None = None,
    text_items: list[dict] | None = None,
    # Shared resources
    hex_to_int: dict | None = None,
    url_to_hex: dict | None = None,
) -> dict:
    """Evaluate a single LiveVQA question. Returns a result dict."""
    async with semaphore:
        t0 = time.time()
        error = None
        raw_response = ""
        n_images = 0
        n_chunks = 0

        try:
            if mode == "naive":
                # No retrieval: editorial photo + question only
                photo = (
                    resolve_editorial_photo(row, args.livevqa_images)
                    if args.include_editorial_photo
                    else None
                )
                images = [photo] if photo else []
                prompt = build_naive_prompt(
                    row["question"], row["options"], has_photo=bool(photo)
                )
                messages = build_messages_for_livevqa(
                    prompt, image_paths=images if images else None
                )
                n_images = len(images)

            elif mode == "pixel":
                items = pixel_items or []
                images, prompt = resolve_pixel_context(
                    row,
                    items,
                    args.top_k,
                    args.include_editorial_photo,
                    args.livevqa_images,
                    args.tiles_dir,
                )
                # Check if we have any retrieved tiles (beyond just the editorial photo)
                has_photo = args.include_editorial_photo and resolve_editorial_photo(
                    row, args.livevqa_images
                )
                n_tile_images = len(images) - (1 if has_photo else 0)
                if n_tile_images <= 0:
                    error = "no_tiles"
                messages = (
                    build_messages_for_livevqa(prompt, image_paths=images)
                    if not error
                    else []
                )
                n_images = len(images)

            elif mode == "text":
                items = text_items or []
                imgs, passages, prompt = resolve_text_context(
                    row,
                    items,
                    args.top_k,
                    args.include_editorial_photo,
                    args.livevqa_images,
                    args.chunks_db,
                    hex_to_int,
                    url_to_hex,
                )
                if not passages:
                    error = "no_chunks"
                messages = (
                    build_messages_for_livevqa(
                        prompt, image_paths=imgs if imgs else None
                    )
                    if not error
                    else []
                )
                n_chunks = len(passages)
                n_images = len(imgs) if imgs else 0

            elif mode == "hybrid":
                # Pixel items -> tile paths; text items -> text passages
                p_items = pixel_items or []
                t_items = text_items or []

                photo = (
                    resolve_editorial_photo(row, args.livevqa_images)
                    if args.include_editorial_photo
                    else None
                )
                tile_paths: list[str] = []
                for it in p_items[: args.top_k]:
                    p = resolve_strip_path(it["hex"], it["file"], args.tiles_dir)
                    if p:
                        tile_paths.append(p)

                chunks: list[str] = []
                for it in t_items[: args.top_k]:
                    if "text" in it and it["text"]:
                        chunks.append(it["text"])

                if not tile_paths and not chunks:
                    error = "no_retrieval"
                else:
                    image_paths = ([photo] if photo else []) + tile_paths
                    prompt = build_hybrid_prompt(
                        row["question"],
                        row["options"],
                        len(tile_paths),
                        len(chunks),
                        has_photo=bool(photo),
                    )
                    messages = build_messages_for_livevqa(
                        prompt,
                        image_paths=image_paths if image_paths else None,
                        text_chunks=chunks if chunks else None,
                    )
                    n_images = len(image_paths)
                    n_chunks = len(chunks)
                if error:
                    messages = []

            else:
                raise ValueError(f"Unknown mode: {mode}")

            if not error:
                raw_response, _usage = await llm_client.generate(messages)

        except Exception as e:
            error = type(e).__name__
            logger.debug("Error on idx=%d: %s", idx, e)

        latency = time.time() - t0
        gt = row.get("ground_truth", "")
        predicted = extract_letter(raw_response) if not error else ""
        is_correct = predicted == gt

        return {
            "idx": idx,
            "question": row["question"],
            "img_path": row.get("img_path", ""),
            "corpus_url": row.get("corpus_url", ""),
            "source": row.get("source", ""),
            "level": row.get("level", ""),
            "ground_truth": gt,
            "predicted": predicted,
            "raw_response": raw_response,
            "correct": is_correct,
            "error": error,
            "n_images": n_images,
            "n_chunks": n_chunks,
            "latency": round(latency, 2),
            "mode": mode,
        }
