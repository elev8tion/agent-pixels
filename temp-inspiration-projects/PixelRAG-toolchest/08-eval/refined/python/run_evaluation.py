async def run_evaluation(args: argparse.Namespace):
    """Main evaluation loop."""
    # Load dataset
    rows = load_livevqa_dataset(args.v4, args.max_samples)

    # Apply option shuffling if requested
    if args.shuffle_seed is not None:
        for i, q in enumerate(rows):
            q["options"], q["ground_truth"] = shuffle_options(
                q["options"],
                q["ground_truth"],
                args.shuffle_seed + i,
            )
        logger.info("Shuffled options with seed=%d", args.shuffle_seed)

    mode = args.mode

    # ---- Retrieval phase (batch, synchronous) ----
    # Build queries for retrieval modes
    pixel_results_map: dict[int, list[dict]] = {}
    text_results_map: dict[int, list[dict]] = {}

    if mode in ("pixel", "hybrid"):
        logger.info("=== Pixel retrieval phase ===")
        queries = []
        for row in rows:
            q: dict = {"text": row["question"]}
            if args.query_instruction:
                q["text"] = f"{args.query_instruction} {q['text']}"
            if args.multimodal_query:
                photo = resolve_editorial_photo(row, args.livevqa_images)
                if photo:
                    with open(photo, "rb") as f:
                        q["image"] = base64.b64encode(f.read()).decode()
            queries.append(q)
        pixel_results = batch_retrieve_pixel(
            queries,
            args.pixel_api,
            search_k=args.search_k,
            top_k=args.retrieval_top_k,
            batch_size=args.retrieval_batch_size,
            nprobe=args.nprobe,
            timeout=args.retrieval_timeout,
            db_path=args.pages_db,
        )
        for i, items in enumerate(pixel_results):
            pixel_results_map[i] = items
        logger.info("Pixel retrieval complete: %d queries", len(pixel_results))

    if mode in ("text", "hybrid"):
        logger.info("=== Text retrieval phase ===")
        queries = []
        for row in rows:
            q = {"text": row["question"]}
            if args.multimodal_query:
                photo = resolve_editorial_photo(row, args.livevqa_images)
                if photo:
                    with open(photo, "rb") as f:
                        q["image"] = base64.b64encode(f.read()).decode()
            queries.append(q)
        text_results = batch_retrieve_text(
            queries,
            args.text_api,
            search_k=args.search_k,
            top_k=args.retrieval_top_k,
            batch_size=args.retrieval_batch_size,
            nprobe=args.nprobe,
            timeout=args.retrieval_timeout,
        )
        for i, items in enumerate(text_results):
            text_results_map[i] = items
        logger.info("Text retrieval complete: %d queries", len(text_results))

    # ---- Load shared resources for cross-format lookups ----
    hex_to_int = None
    url_to_hex = None
    if mode in ("text",) and args.chunks_db and os.path.exists(args.chunks_db):
        if args.hex_to_int_map and os.path.exists(args.hex_to_int_map):
            hex_to_int = load_hex_to_int(args.hex_to_int_map)
            logger.info("Loaded hex->int map: %d entries", len(hex_to_int))
        if args.pages_db and os.path.exists(args.pages_db):
            url_to_hex = load_url_to_hex(args.pages_db)
            logger.info("Loaded url->hex map: %d entries", len(url_to_hex))

    # ---- Reader phase (async, concurrent) ----
    logger.info("=== Reader phase: mode=%s, model=%s ===", mode, args.model)
    llm_client = LLMClient(
        model=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        temperature=0.0,
        max_tokens=args.max_tokens,
        timeout=args.reader_timeout,
        enable_thinking=False if args.no_think else None,
    )

    # Smoke test
    logger.info("Smoke test on first example...")
    sem = asyncio.Semaphore(args.workers)
    smoke_result = await evaluate_one(
        0,
        rows[0],
        llm_client,
        mode,
        args,
        sem,
        pixel_items=pixel_results_map.get(0),
        text_items=text_results_map.get(0),
        hex_to_int=hex_to_int,
        url_to_hex=url_to_hex,
    )
    if smoke_result["error"]:
        logger.warning("Smoke test had error: %s", smoke_result["error"])
    else:
        logger.info(
            "Smoke test OK: pred=%s gt=%s correct=%s latency=%.1fs",
            smoke_result["predicted"],
            smoke_result["ground_truth"],
            smoke_result["correct"],
            smoke_result["latency"],
        )

    # Prepare output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Checkpoint handling
    out_s = str(output_path)
    if out_s.endswith(".jsonl"):
        checkpoint_path = out_s[:-6] + "_checkpoint.jsonl"
    elif out_s.endswith(".json"):
        checkpoint_path = out_s[:-5] + "_checkpoint.json"
    else:
        checkpoint_path = out_s + "_checkpoint.jsonl"
    completed: dict[int, dict] = {}
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path) as f:
            for line in f:
                r = json.loads(line)
                completed[r["idx"]] = r
        logger.info("Loaded checkpoint: %d completed rows", len(completed))

    # Run all examples
    tasks = []
    for i, row in enumerate(rows):
        if i in completed:
            continue
        tasks.append(
            evaluate_one(
                i,
                row,
                llm_client,
                mode,
                args,
                sem,
                pixel_items=pixel_results_map.get(i),
                text_items=text_results_map.get(i),
                hex_to_int=hex_to_int,
                url_to_hex=url_to_hex,
            )
        )

    # Process with progress tracking
    results: list[dict] = list(completed.values())
    correct = sum(1 for r in results if r["correct"])
    total = len(results)
    errors = sum(1 for r in results if r["error"])
    err_types: dict[str, int] = defaultdict(int)
    for r in results:
        if r["error"]:
            err_types[r["error"]] += 1
    level_stats: dict = defaultdict(lambda: {"correct": 0, "total": 0})
    for r in results:
        lvl = r.get("level", "?")
        level_stats[lvl]["total"] += 1
        if r["correct"]:
            level_stats[lvl]["correct"] += 1

    latencies: list[float] = [r["latency"] for r in results if not r["error"]]
    t0 = time.time()
    last_log = t0
    fi = 0
    total_tasks = len(tasks) + len(completed)

    # Save checkpoint incrementally
    ckpt_fh = open(checkpoint_path, "a")

    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        total += 1
        fi += 1

        if result["error"]:
            errors += 1
            err_types[result["error"]] += 1
        else:
            latencies.append(result["latency"])
        if result["correct"]:
            correct += 1
        lvl = result.get("level", "?")
        level_stats[lvl]["total"] += 1
        if result["correct"]:
            level_stats[lvl]["correct"] += 1

        # Write checkpoint
        ckpt_fh.write(json.dumps(result) + "\n")
        if fi % 500 == 0:
            ckpt_fh.flush()

        # Log progress
        now = time.time()
        if fi % 200 == 0 or now - last_log > 30 or fi == len(tasks):
            el = now - t0
            qps = fi / el if el > 0 else 0
            acc = correct / total * 100 if total else 0
            p50 = sorted(latencies)[len(latencies) // 2] if latencies else 0
            eta = (len(tasks) - fi) / qps if qps > 0 else 0
            logger.info(
                "[%d/%d] acc=%.2f%% | %.1f q/s ETA %dm%ds | "
                "lat p50=%.1fs | err=%d (%s)",
                total,
                total_tasks,
                acc,
                qps,
                int(eta) // 60,
                int(eta) % 60,
                p50,
                errors,
                dict(err_types),
            )
            last_log = now

    ckpt_fh.close()

    # ---- Sort results by idx and write final output ----
    results.sort(key=lambda r: r["idx"])

    acc = correct / total * 100 if total else 0
    elapsed = time.time() - t0

    # Print summary
    print(f"\n{'=' * 64}")
    print(f"LiveVQA Evaluation — mode={mode}")
    print(f"{'=' * 64}")
    print(f"Model: {args.model}")
    print(f"Total: {total}  Correct: {correct}  Accuracy: {acc:.2f}%")
    print(f"Errors: {errors} ({dict(err_types)})")
    print(f"Time: {elapsed:.0f}s ({total / elapsed:.1f} q/s)" if elapsed > 0 else "")
    if latencies:
        ls = sorted(latencies)
        print(
            f"Latency: p50={ls[len(ls) // 2]:.2f}s "
            f"p90={ls[int(len(ls) * 0.9)]:.2f}s "
            f"p99={ls[int(len(ls) * 0.99)]:.2f}s"
        )
    print()
    print("By difficulty level:")
    for lvl in sorted(level_stats.keys()):
        s = level_stats[lvl]
        la = s["correct"] / s["total"] * 100 if s["total"] else 0
        print(f"  Level {lvl}: {s['correct']}/{s['total']} = {la:.1f}%")

    # By news source (outlet)
    source_stats: dict = defaultdict(lambda: {"correct": 0, "total": 0})
    for r in results:
        src = r.get("source", "?")
        outlet = src.split()[0] if src else "?"  # "CNN Politics" -> "CNN"
        source_stats[outlet]["total"] += 1
        if r["correct"]:
            source_stats[outlet]["correct"] += 1
    print("\nBy outlet:")
    for outlet in sorted(source_stats.keys()):
        s = source_stats[outlet]
        la = s["correct"] / s["total"] * 100 if s["total"] else 0
        print(f"  {outlet}: {s['correct']}/{s['total']} = {la:.1f}%")

    # Write final JSONL output
    with open(args.output, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    logger.info("Saved %d results to %s", len(results), args.output)

    # Write summary JSON (alongside the JSONL)
    out_str = str(args.output)
    if out_str.endswith(".jsonl"):
        summary_path = out_str[:-6] + "_summary.json"
    elif out_str.endswith(".json"):
        summary_path = out_str[:-5] + "_summary.json"
    else:
        summary_path = out_str + "_summary.json"
    summary = {
        "mode": mode,
        "model": args.model,
        "total": total,
        "correct": correct,
        "accuracy": acc,
        "errors": errors,
        "error_types": dict(err_types),
        "elapsed_s": elapsed,
        "top_k": args.top_k,
        "include_editorial_photo": args.include_editorial_photo,
        "multimodal_query": args.multimodal_query,
        "shuffle_seed": args.shuffle_seed,
        "v4_source": args.v4,
        "level_stats": {str(k): v for k, v in level_stats.items()},
        "outlet_stats": {k: v for k, v in source_stats.items()},
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info("Saved summary to %s", summary_path)

    # Clean up checkpoint
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)
        logger.info("Removed checkpoint %s", checkpoint_path)
