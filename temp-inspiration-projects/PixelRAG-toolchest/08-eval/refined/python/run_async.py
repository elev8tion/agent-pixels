async def run_async(args):
    """Main async entry point."""
    # 1. Load data
    if args.task == "simpleqa":
        examples = load_simpleqa_wikipedia(
            args.num_examples,
            verified=args.verified,
            no_wiki_filter=getattr(args, "no_wiki_filter", False),
        )
    elif args.task == "encyclopedic_vqa":
        split = args.subset or "val"
        examples = load_encyclopedic_vqa_data(
            split,
            args.num_examples,
            dataset_filter=args.evqa_dataset_filter,
            question_type_filter=args.evqa_question_type_filter,
            local_path=args.evqa_data_path,
        )
        if args.evqa_instruction_override is not None:
            for ex in examples:
                ex["additional_instructions"] = args.evqa_instruction_override
    elif args.task == "worldvqa":
        examples = load_worldvqa_data(
            args.num_examples, language_filter=getattr(args, "worldvqa_language", None)
        )
    elif args.task == "2wiki":
        dataset_repo = DATASET_REPOS["2wiki"]
        examples = load_shortformqa_data(dataset_repo, args.num_examples)
    elif args.task == "simplevqa":
        examples = load_simplevqa_data(args.num_examples)
    elif args.task == "factualvqa":
        examples = load_factualvqa_data(args.num_examples)
    elif args.task == "mmsearch":
        examples = load_mmsearch_data(args.num_examples)
    elif args.task == "webqa":
        examples = load_webqa_data(args.num_examples)
    elif args.task == "multimodalqa":
        examples = load_multimodalqa_data(args.num_examples)
    elif args.task == "nq":
        examples = load_nq_data(
            args.num_examples, split=getattr(args, "nq_split", "validation")
        )
    elif args.task == "triviaqa":
        examples = load_triviaqa_data(args.num_examples)
    elif args.task == "nq_tables":
        examples = load_nq_tables_data(args.num_examples)
    elif args.task == "piqa":
        examples = load_piqa_data(args.num_examples)
    elif args.task == "hellaswag":
        examples = load_hellaswag_data(args.num_examples)
    elif args.task == "commonsense_qa":
        examples = load_commonsenseqa_data(args.num_examples)
    elif args.task == "openbookqa":
        examples = load_openbookqa_data(args.num_examples)
    elif args.task == "arc_easy":
        examples = load_arc_data("ARC-Easy", args.num_examples)
    elif args.task == "arc_challenge":
        examples = load_arc_data("ARC-Challenge", args.num_examples)
    else:
        raise ValueError(f"Unsupported task: {args.task}.")

    # Stamp each example with its 0-indexed position in the loaded list so
    # process_example() can record it. Async writes append in completion order, not
    # load order — load_index lets downstream `sorted(records, key=lambda r: r["load_index"])`
    # recover the canonical order and gives a true line-level prefix property
    # (n=200 records are exactly load_index ∈ [0, 200) of an n=1000 run).
    for _idx, _ex in enumerate(examples):
        _ex["_load_index"] = _idx

    # Build the per-run reproducibility metadata once, after dataset is loaded so
    # we know n_loaded. Stamped on every JSONL record by process_example().
    run_metadata = _build_run_metadata(args, n_loaded=len(examples))
    print(
        f"\n[run_metadata] task={run_metadata['task']} split={run_metadata['split']} "
        f"n_requested={run_metadata['num_examples_requested']} n_loaded={run_metadata['num_examples_loaded']} "
        f"retrieval_top_k={run_metadata['retrieval_top_k']} reader_top_k={run_metadata['reader_top_k']} "
        f"reader={run_metadata['reader_model']}"
    )
    for api_key in ("local_api_status", "text_api_status"):
        st = run_metadata.get(api_key)
        if st and "_error" not in st:
            print(
                f"[run_metadata] {api_key}: vec={st.get('total_vectors')} "
                f"built_at={st.get('index_built_at')} model={st.get('model')}"
            )
        elif st:
            print(f"[run_metadata] {api_key}: ERROR {st.get('_error')}")

    if args.task in ("nq", "triviaqa", "nq_tables"):
        for ex in examples:
            ex["additional_instructions"] = (
                "Answer with as few words as possible. Give only the answer, no explanation."
            )

    if args.reader_extra_instructions:
        for ex in examples:
            base = ex.get("additional_instructions") or ""
            ex["additional_instructions"] = (
                base + "\n\n" + args.reader_extra_instructions
            ).strip()

    if args.reader_few_shot_json:
        with open(args.reader_few_shot_json) as _fsf:
            _demos = json.load(_fsf)
        for ex in examples:
            ex["_reader_few_shot"] = _demos
        logger.info(
            f"Loaded {len(_demos)} few-shot demo(s) from {args.reader_few_shot_json}"
        )

    # Get model configuration
    model_config = get_model_config(args.model)

    # Handle OpenRouter API
    if args.open_router:
        api_base = "https://openrouter.ai/api/v1"
        if args.api_key and args.api_key != "dummy":
            api_key = args.api_key
        else:
            api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key == "dummy":
            raise ValueError(
                "OpenRouter API key required. Set --api-key or OPENROUTER_API_KEY environment variable."
            )
        logger.info(f"Using OpenRouter API with model: {args.model}")
        model = args.model
    elif args.commonstack:
        api_base = "https://api.commonstack.ai/v1"
        if args.api_key and args.api_key != "dummy":
            api_key = args.api_key
        else:
            api_key = os.getenv("COMMONSTACK_API_KEY")
        if not api_key or api_key == "dummy":
            raise ValueError(
                "Commonstack API key required. Set --api-key or COMMONSTACK_API_KEY environment variable."
            )
        logger.info(f"Using Commonstack API with model: {args.model}")
        model = args.model
    else:
        # Override with command-line args if provided
        # For Gemini, api_base from config is None, so use command-line arg or default
        api_base = (
            args.api_base
            if args.api_base
            else (model_config["api_base"] or "http://localhost:8000/v1")
        )
        api_key = args.api_key if args.api_key else model_config["api_key"]
        model = model_config["model"]

    # Generate output filename with model name if output is not explicitly set
    if not args.output or args.output == "auto":
        # Determine mode for filename
        if args.url_screenshot:
            mode_str = "screenshot"
        elif args.url_tiled_screenshot and args.local_wiki:
            mode_str = "tiled_screenshot_localwiki"
        elif args.url_tiled_screenshot:
            mode_str = "tiled_screenshot"
        elif args.url_text:
            mode_str = f"text_{args.text_source}"
        elif args.retrieval_augment:
            if args.use_colqwen_retrieval:
                mode_str = "vector_colqwen"
            else:
                mode_str = "vector_jina"
        elif args.use_tiled_retrieval:
            if args.use_colqwen_retrieval:
                mode_str = "tiled_vector_colqwen"
            elif args.use_qwen3vl_embedding:
                mode_str = "tiled_vector_qwen3vl_embedding"
                if args.local_wiki:
                    mode_str += "_localwiki"
                if args.task == "encyclopedic_vqa":
                    if args.evqa_multimodal_query:
                        if args.evqa_multimodal_query_text_only:
                            mode_str += "_multimodal_textonly"
                        elif args.evqa_multimodal_query_image_only:
                            mode_str += "_multimodal_imageonly"
                        else:
                            mode_str += "_multimodal"
                    else:
                        mode_str += "_querycard"
                elif args.pixel_query:
                    mode_str += "_pixelq"
                if args.pixel_compress_ratio and args.pixel_compress_ratio > 1:
                    mode_str += f"_compress{args.pixel_compress_ratio}x"
            else:
                mode_str = "tiled_vector_jina"
        elif args.text_api:
            mode_str = "text_api"
        elif args.html_dom_lookup:
            mode_str = "html_dom_lookup"
        elif args.hybrid:
            mode_str = "hybrid"
        elif args.text_vector:
            if args.text_source == "ds-serve":
                mode_str = "text_vector_ds_serve"
            else:
                mode_str = f"text_vector_{args.text_source}_{args.text_embed_preset}"
        else:
            mode_str = (
                "no_retrieval"
                if args.task in ("encyclopedic_vqa", "worldvqa")
                else "naive"
            )
            if args.task == "2wiki":
                mode_str = "naive"

        output_dir = "eval_output"
        args.output = get_output_filename(
            output_dir=output_dir,
            model_name=model,
            mode=mode_str,
            num_examples=args.num_examples or len(examples),
            url_screenshot=args.url_screenshot,
            task=args.task,
        )

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Check if output file exists
    if os.path.exists(args.output) and os.path.getsize(args.output) > 0:
        if not args.force:
            print(
                f"Error: Output file '{args.output}' already exists and is not empty."
            )
            print("Use --force to overwrite.")
            sys.exit(1)
        else:
            print(f"Warning: Overwriting existing file '{args.output}'")

    # Clear output file
    with open(args.output, "w"):
        pass

    # 2. Initialize retriever (each retriever uses data layer internally)
    # Tile width is fixed to 1024 (matches screenshot width)
    TILE_WIDTH = 1024

    # Set default tiles_dir if not specified
    if args.tiles_dir is None:
        args.tiles_dir = f"tiles-{TILE_WIDTH}x{args.tile_height}"

    # Calculate max_tiles from context length if not specified
    # Qwen3-VL: 1024x1024 tile = 1024 image tokens + ~10 overhead = ~1034 tokens
    # Scale by tile height ratio
    BASE_TOKENS_PER_TILE = 1050  # for 1024x1024
    TOKENS_PER_TILE = int(BASE_TOKENS_PER_TILE * args.tile_height / 1024)
    RESERVED_TOKENS = 2000  # For question and response
    if args.max_tiles is None and (
        args.url_tiled_screenshot or args.use_tiled_retrieval
    ):
        available_tokens = args.model_context_length - RESERVED_TOKENS
        args.max_tiles = max(1, available_tokens // TOKENS_PER_TILE)
        logger.info(
            f"Auto-calculated max_tiles: {args.max_tiles} (context={args.model_context_length}, per_tile={TOKENS_PER_TILE}, tile={TILE_WIDTH}x{args.tile_height})"
        )

    from lib.retrievers import build_retriever

    retriever, mode = build_retriever(args, examples, model, api_base, api_key)
    # (retriever selection logic moved to simpleqa/retriever_factory.py)
    # 3. Initialize LLM client
    llm_client = LLMClient(
        model=model,
        api_base=api_base,
        api_key=api_key,
        max_tokens=args.max_tokens,
        max_context_tokens=args.model_context_length,
        timeout=args.timeout,
        enable_thinking=(False if args.no_think else None),
        force_openai_compat=(args.open_router or args.commonstack),
    )

    # 3b. Create pixel-compressed encoder for generation if requested
    gen_encode_fn = None
    if args.pixel_compress_ratio and args.pixel_compress_ratio > 1:
        gen_encode_fn = make_compressed_encoder(args.pixel_compress_ratio)
        mode += f" (PixelCompress={args.pixel_compress_ratio}x)"
        logger.info(f"Generation pixel compression: {args.pixel_compress_ratio}x")

    # 3c. Prefetch retrieval results for batch-capable retrievers
    if hasattr(retriever, "prefetch"):
        print("Prefetching retrieval results (batch API call)...")
        await retriever.prefetch(examples)

    # 4. Process examples
    total_examples = len(examples)
    logger.info(
        f"Processing {total_examples} examples (Mode: {mode}, Concurrency: {args.max_concurrent})"
    )
    print(f"\n{'=' * 80}")
    print(
        f"Starting evaluation: {total_examples} examples with max {args.max_concurrent} concurrent requests"
    )
    if gen_encode_fn:
        print(
            f"Pixel compression for generation: {args.pixel_compress_ratio}x (retrieval at original resolution)"
        )
    print(f"{'=' * 80}\n")

    semaphore = asyncio.Semaphore(args.max_concurrent)

    # Progress counter (shared dict for async updates)
    progress_counter = {"completed": 0, "start_time": time.time()}

    tiles_dir = getattr(retriever, "tiles_dir", None) or (
        args.tiles_dir if hasattr(args, "tiles_dir") else None
    )
    if args.react and args.local_api:
        tasks = [
            process_example_react(
                llm_client,
                retriever,
                ex,
                semaphore,
                args.output,
                progress_counter,
                total_examples,
                encode_image_fn=gen_encode_fn,
                task_name=args.task,
                tiles_dir=tiles_dir,
                max_turns=args.react_max_turns,
                api_url=args.local_api_url,
                react_top_k=args.retrieval_top_k,
                nprobe=args.nprobe,
                prompt_version=args.react_prompt,
            )
            for ex in examples
        ]
    else:
        tasks = [
            process_example(
                llm_client,
                retriever,
                ex,
                semaphore,
                args.output,
                progress_counter,
                total_examples,
                encode_image_fn=gen_encode_fn,
                task_name=args.task,
                tiles_dir=tiles_dir,
                run_metadata=run_metadata,
            )
            for ex in examples
        ]

    results = await tqdm_asyncio.gather(*tasks)

    # Print completion summary
    elapsed_time = time.time() - progress_counter["start_time"]
    print(f"\n{'=' * 80}")
    print(
        f"Evaluation completed: {progress_counter['completed']}/{total_examples} examples in {elapsed_time:.1f}s"
    )
    print(
        f"Average time per example: {elapsed_time / max(1, progress_counter['completed']):.2f}s"
    )
    print(f"{'=' * 80}\n")

    # 5. Print statistics
    print_statistics(results, args)
