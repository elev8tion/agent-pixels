def _build_run_metadata(args, n_loaded: int) -> dict:
    """Build the per-run reproducibility tuple stamped into every JSONL record.

    See root CLAUDE.md "Reproducibility tagging" — every benchmark number must
    carry: dataset+split+n, reader, retriever+checkpoint, index path+vec+built_at,
    top-k, query instruction, grader.
    """
    import datetime
    import subprocess

    reader_top_k = (
        args.reader_top_k if args.reader_top_k is not None else args.retrieval_top_k
    )
    meta = {
        "schema_version": 1,
        "run_started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        # Dataset + split + n
        "task": args.task,
        "split": getattr(args, "nq_split", None)
        if args.task == "nq"
        else _DEFAULT_SPLIT_FOR_TASK.get(args.task, "unknown"),
        "num_examples_requested": args.num_examples,
        "num_examples_loaded": n_loaded,
        # Reader
        "reader_model": args.model,
        "reader_max_tokens": getattr(args, "max_tokens", None),
        "reader_no_think": getattr(args, "no_think", False),
        "reader_extra_instructions": getattr(args, "reader_extra_instructions", None),
        # Retrieval k vs reader k (decoupled)
        "retrieval_top_k": args.retrieval_top_k,
        "reader_top_k": reader_top_k,
        # Query instruction (verbatim)
        "query_instruction": getattr(args, "query_instruction", None),
        # Retrieval API URLs + their /status (captures index path, vec count, built_at, model)
        "local_api_url": getattr(args, "local_api_url", None),
        "text_api_url": getattr(args, "text_api_url", None),
        "local_api_status": _fetch_status(getattr(args, "local_api_url", None)),
        "text_api_status": _fetch_status(getattr(args, "text_api_url", None)),
        # Misc dataset flags that change semantics
        "verified": getattr(args, "verified", False),
        "no_wiki_filter": getattr(args, "no_wiki_filter", False),
    }
    try:
        meta["git_commit"] = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except Exception:  # noqa: BLE001
        meta["git_commit"] = None
    return meta
