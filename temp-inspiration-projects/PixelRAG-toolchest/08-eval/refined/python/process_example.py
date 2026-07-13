async def process_example(
    llm_client: LLMClient,
    retriever,
    example: dict,
    semaphore: asyncio.Semaphore,
    output_file: str | None = None,
    progress_counter: dict | None = None,
    total_examples: int = 0,
    encode_image_fn=None,
    task_name: str = "simpleqa",
    tiles_dir: str | None = None,
    run_metadata: dict | None = None,
) -> dict | None:
    """Process a single example: retrieve -> build messages -> call LLM."""
    async with semaphore:
        try:
            example_id = example.get("id", "unknown")
            # logger.info(f"Starting processing example {example_id}")

            # 1. Retrieve (data preparation happens inside retriever if needed)
            logger.debug(f"Retrieving for example {example_id}")
            retrieval_start_time = time.time()
            retrieval_result = await retriever.retrieve(example["problem"], example)
            retrieval_time = time.time() - retrieval_start_time
            logger.debug(
                f"Retrieval complete for example {example_id} (took {retrieval_time:.2f}s)"
            )

            # 1a. Snapshot the full retrieved set BEFORE reader-side slicing.
            # The JSONL records the full set so downstream grading can re-derive k=1/2/3
            # from a single retrieval-top-k=K_max run without re-querying the index.
            retrieved_full_images = (
                list(retrieval_result.images) if retrieval_result.images else []
            )
            retrieved_full_image_urls = list(
                getattr(retrieval_result, "image_urls", []) or []
            )
            # 1b. Reader-side top-k (decoupled from retrieval-k). Slice in place so build_messages
            # and the LLM see only the first reader_top_k items.
            reader_top_k = (run_metadata or {}).get("reader_top_k")
            if (
                reader_top_k is not None
                and retrieval_result.images
                and reader_top_k < len(retrieval_result.images)
            ):
                retrieval_result.images = retrieval_result.images[:reader_top_k]
                if getattr(retrieval_result, "image_urls", None):
                    retrieval_result.image_urls = retrieval_result.image_urls[
                        :reader_top_k
                    ]
                urls = []
                seen_urls = set()
                for url in getattr(retrieval_result, "image_urls", []) or []:
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        urls.append(url)
                if not urls and retrieval_result.source_url:
                    for url in retrieval_result.source_url.split(", "):
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            urls.append(url)
                        if len(urls) >= reader_top_k:
                            break
                if urls:
                    retrieval_result.source_url = ", ".join(urls)

            # 1b. Attach query image so VLM sees it alongside retrieved tiles
            if not retrieval_result.query_image_path and retrieval_result.has_content:
                if task_name == "encyclopedic_vqa":
                    tiles_dir = getattr(retriever, "tiles_dir", None) or "tiles/evqa"
                    img_path = _get_query_image_path_for_example(
                        example, tiles_dir, quiet=True
                    )
                    if img_path:
                        retrieval_result.query_image_path = img_path
                elif task_name in (
                    "worldvqa",
                    "simplevqa",
                    "factualvqa",
                    "mmsearch",
                    "webqa",
                    "multimodalqa",
                ):
                    img_path = _save_task_query_image(
                        example, task_name, base_dir="tiles"
                    )
                    if img_path:
                        retrieval_result.query_image_path = img_path

            # 2. Build messages
            logger.debug(f"Building messages for example {example_id}")
            _encode_fn = (
                encode_image_fn if encode_image_fn is not None else encode_screenshot
            )
            messages = build_messages(
                query=example["problem"],
                retrieval_result=retrieval_result,
                encode_image_fn=_encode_fn,
                additional_instructions=example.get("additional_instructions"),
                few_shot_demos=example.get("_reader_few_shot"),
            )
            logger.debug(f"Messages built for example {example_id}")

            # 3. Call LLM
            # logger.info(f"Calling LLM for example {example_id}")
            llm_start_time = time.time()
            generated_text, usage = await llm_client.generate(messages)
            llm_time = time.time() - llm_start_time

            # Update progress counter
            if progress_counter is not None:
                progress_counter["completed"] += 1
                completed = progress_counter["completed"]
                ((completed / total_examples * 100) if total_examples > 0 else 0)

                # Accumulate timing stats
                if "retrieval_times" not in progress_counter:
                    progress_counter["retrieval_times"] = []
                    progress_counter["llm_times"] = []
                progress_counter["retrieval_times"].append(retrieval_time)
                progress_counter["llm_times"].append(llm_time)

            # 4. Build result
            result = {
                "example_id": example["id"],
                # 0-indexed position in the loaded examples list — see run_async() stamping.
                # Async writes append in completion order; sort downstream by load_index
                # to recover canonical load order and the strict line-level prefix property
                # (records with load_index < N are exactly the first N loaded examples).
                "load_index": example.get("_load_index"),
                "problem": example["problem"],
                "model": llm_client.model,
                "final_response": generated_text,
                "original_data": {
                    k: v
                    for k, v in example.items()
                    if not hasattr(v, "save") and not k.startswith("_")
                },
                "full_traces": {},
                "dataset_name": task_name,
                "retrieval_type": retrieval_result.retrieval_type,
                "has_retrieval_content": retrieval_result.has_content,
                "usage": usage,
                "success": True,
                "timing": {
                    "retrieval_time": retrieval_time,
                    "llm_time": llm_time,
                    "total_time": retrieval_time + llm_time,
                },
                # Per-record reproducibility tag — see root CLAUDE.md "Reproducibility tagging".
                # Stamped on every record so any single line is self-describing.
                "run_metadata": run_metadata,
            }

            # Add retrieval-specific info
            if retrieval_result.source_url:
                result["used_url"] = retrieval_result.source_url
            if retrieval_result.text:
                result["context_length"] = len(retrieval_result.text)
            # `retrieved_images` records the FULL retrieved set (pre reader-side slicing)
            # so downstream grading at k=1/2/3 can be derived from one retrieval_top_k=K_max run.
            if retrieved_full_images:
                result["retrieved_images"] = []
                for idx, (path, score) in enumerate(retrieved_full_images):
                    item = {"path": path, "score": score}
                    if (
                        idx < len(retrieved_full_image_urls)
                        and retrieved_full_image_urls[idx]
                    ):
                        item["url"] = retrieved_full_image_urls[idx]
                    result["retrieved_images"].append(item)
            if retrieval_result.pixel_query_path:
                result["pixel_query_path"] = retrieval_result.pixel_query_path

            # Always include query image path in result for eval analysis
            query_img_path = (
                retrieval_result.query_image_path or retrieval_result.pixel_query_path
            )
            if not query_img_path:
                if task_name == "encyclopedic_vqa" and tiles_dir:
                    query_img_path = _get_query_image_path_for_example(
                        example, tiles_dir
                    )
                elif task_name == "worldvqa":
                    query_img_path = _save_worldvqa_query_image(
                        example, base_dir="tiles"
                    )
                elif task_name in (
                    "simplevqa",
                    "factualvqa",
                    "mmsearch",
                    "webqa",
                    "multimodalqa",
                ):
                    query_img_path = _save_task_query_image(
                        example, task_name, base_dir="tiles"
                    )
            if query_img_path:
                result["query_image_path"] = query_img_path

            # Record compressed image paths if pixel compression was used
            if (
                _encode_fn is not None
                and hasattr(_encode_fn, "compressed_paths")
                and retrieval_result.images
            ):
                compressed_images = []
                for orig_path, score in retrieval_result.images:
                    comp_path = _encode_fn.compressed_paths.get(orig_path)
                    if comp_path:
                        compressed_images.append(
                            {
                                "original_path": orig_path,
                                "compressed_path": comp_path,
                                "score": score,
                            }
                        )
                if compressed_images:
                    result["compressed_images"] = compressed_images
                    result["pixel_compress_ratio"] = _encode_fn.compress_ratio
                    result["compressed_images_dir"] = _encode_fn.save_dir

            # Incremental save
            if output_file:
                with open(output_file, "a") as f:
                    f.write(json.dumps(result) + "\n")

            return result

        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            example_id = example.get("id", "unknown")

            # Update progress counter even on error
            if progress_counter is not None:
                progress_counter["completed"] += 1
                logger.warning(f"Example {example_id} failed: {e}")

            logger.error(f"Error processing {example_id}: {e}")
            logger.error(f"Traceback: {error_trace}")
            result = {
                "example_id": example.get("id"),
                "problem": example.get("problem"),
                "model": llm_client.model,
                "final_response": None,
                "original_data": {
                    k: v
                    for k, v in example.items()
                    if not hasattr(v, "save") and not k.startswith("_")
                },
                "dataset_name": task_name,
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "timing": {
                    "retrieval_time": None,
                    "llm_time": None,
                    "total_time": None,
                },
            }
            if output_file:
                with open(output_file, "a") as f:
                    f.write(json.dumps(result) + "\n")
            return result
