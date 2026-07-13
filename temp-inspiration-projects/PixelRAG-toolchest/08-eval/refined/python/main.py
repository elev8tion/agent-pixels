def main() -> None:
    ap = argparse.ArgumentParser(
        description="MoNaCo multi-hop QA evaluation with ReAct agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--reader",
        type=str,
        default="gpt-5",
        help="Model name (default: gpt-5). E.g. gpt-5, gpt-4o-2024-08-06, claude-sonnet-4-6.",
    )
    ap.add_argument(
        "--retrieval",
        type=str,
        choices=["text", "pixel"],
        default="text",
        help="Retrieval backend: 'text' (default) or 'pixel'.",
    )
    ap.add_argument(
        "--data-path",
        type=str,
        default=str(DEFAULT_DATA_PATH),
        help=f"Path to MoNaCo JSONL file (default: {DEFAULT_DATA_PATH})",
    )
    ap.add_argument(
        "--output-dir",
        type=str,
        default="",
        help="Override output directory (default: eval_output/monaco/<tag>)",
    )
    ap.add_argument(
        "--limit", type=int, default=0, help="Process only first N examples (0 = all)"
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of concurrent workers (default: 4)",
    )
    ap.add_argument(
        "--smoke", type=int, default=0, help="Quick smoke test with N examples"
    )
    ap.add_argument(
        "--tag-suffix",
        type=str,
        default="",
        help="Appended to the auto-generated run tag",
    )
    ap.add_argument("--base-url", type=str, default="", help="Override OPENAI_BASE_URL")
    ap.add_argument(
        "--api-key",
        type=str,
        default="",
        help="Override OPENAI_API_KEY / ANTHROPIC_API_KEY",
    )
    ap.add_argument(
        "--pixel-api",
        type=str,
        default="",
        help=f"Pixel search endpoint (default: {PIXEL_API})",
    )
    ap.add_argument(
        "--text-api",
        type=str,
        default="",
        help=f"Text search endpoint (default: {TEXT_API})",
    )
    ap.add_argument(
        "--image-detail",
        choices=["auto", "low", "high"],
        default="auto",
        help="OpenAI image detail level for pixel retrieval",
    )
    ap.add_argument(
        "--default-top-k",
        type=int,
        default=DEFAULT_K,
        help=f"Default top-k per search (default: {DEFAULT_K})",
    )
    ap.add_argument(
        "--max-top-k",
        type=int,
        default=MAX_TOP_K,
        help=f"Max top-k the agent can use (default: {MAX_TOP_K})",
    )
    ap.add_argument(
        "--max-turns",
        type=int,
        default=MAX_TURNS,
        help=f"Max ReAct turns (default: {MAX_TURNS})",
    )
    ap.add_argument(
        "--judge",
        action="store_true",
        help="Run LLM judge grading after all predictions (secondary metric)",
    )
    ap.add_argument(
        "--judge-model",
        type=str,
        default="gpt-4.1-2025-04-14",
        help="Model for LLM judge (default: gpt-4.1-2025-04-14)",
    )
    ap.add_argument(
        "--judge-workers",
        type=int,
        default=12,
        help="Workers for LLM judge (default: 12)",
    )
    args = ap.parse_args()

    # Set module-level globals
    global _PIXEL_API, _TEXT_API, _DEFAULT_TOP_K, _MAX_TOP_K, _IMAGE_DETAIL
    _PIXEL_API = args.pixel_api or PIXEL_API
    _TEXT_API = args.text_api or TEXT_API
    _DEFAULT_TOP_K = args.default_top_k
    _MAX_TOP_K = args.max_top_k
    _IMAGE_DETAIL = args.image_detail
    globals()["MAX_TURNS"] = args.max_turns

    # Resolve API key
    model = args.reader
    use_claude = _is_claude_model(model)
    if use_claude:
        api_key = (
            args.api_key.strip() or os.environ.get("ANTHROPIC_API_KEY", "")
        ).strip()
        if not api_key:
            raise SystemExit("ANTHROPIC_API_KEY not set (use --api-key or env var)")
        base_url = ""  # unused for Claude
    else:
        api_key = (args.api_key.strip() or os.environ.get("OPENAI_API_KEY", "")).strip()
        if not api_key:
            raise SystemExit("OPENAI_API_KEY not set (use --api-key or env var)")
        base_url = (
            args.base_url.strip()
            or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        ).strip()

    # Build run tag
    model_slug = model.replace("/", "_").replace("-", "_").replace(".", "_")
    tag = f"{model_slug}_agent_{args.retrieval}{args.tag_suffix}"

    # Output directory
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = DEFAULT_OUTPUT_DIR / tag
    out_dir.mkdir(parents=True, exist_ok=True)

    logger = _setup_logging(tag)

    # Load data
    data_path = Path(args.data_path)
    rows = load_monaco(data_path)
    logger.info(f"Reader: {model} | retrieval: {args.retrieval} | tag: {tag}")
    logger.info(f"Data: {data_path} ({len(rows)} examples)")
    if not use_claude:
        logger.info(f"base_url: {base_url}")
    if args.retrieval == "pixel":
        logger.info(f"pixel_api: {_PIXEL_API}")
    else:
        logger.info(f"text_api: {_TEXT_API}")

    # Filter already-done examples (resumable)
    todo = [
        ex
        for ex in rows
        if not (out_dir / f"llm_qa_judgement__{ex['ex_num']}.json").exists()
    ]
    logger.info(
        f"Remaining: {len(todo)} (skipping {len(rows) - len(todo)} already-done)"
    )

    if args.smoke:
        todo = todo[: args.smoke]
    elif args.limit:
        todo = todo[: args.limit]

    if not todo:
        logger.info("Nothing to do.")
    else:
        # Run predictions
        t0 = time.time()
        n_ok = n_err = 0
        f1_sum = 0.0
        n_graded = 0

        with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futs = {
                pool.submit(
                    process_one, ex, model, args.retrieval, api_key, base_url
                ): ex
                for ex in todo
            }
            for i, fut in enumerate(cf.as_completed(futs), 1):
                ex = futs[fut]
                out_path = out_dir / f"llm_qa_judgement__{ex['ex_num']}.json"
                try:
                    rec = fut.result()
                    out_path.write_text(json.dumps(rec, ensure_ascii=False, indent=2))
                    n_ok += 1

                    f1_val = rec.get("token_f1")
                    f1_str = f"F1={f1_val:.3f}" if f1_val is not None else "F1=N/A"
                    if f1_val is not None:
                        f1_sum += f1_val
                        n_graded += 1

                    tail = rec["output"].splitlines()[-1][:120] if rec["output"] else ""
                    msg = (
                        f"  [{i:>4}/{len(todo)}] ex={ex['ex_num']:<5} "
                        f"turns={rec.get('n_turns', '?')} "
                        f"searches={rec.get('n_searches', '?')} "
                        f"t={rec.get('elapsed_sec'):>5.1f}s "
                        f"{f1_str} | {tail}"
                    )
                    logger.info(msg)
                except Exception as e:
                    n_err += 1
                    tb = traceback.format_exc()
                    msg = f"  [{i:>4}/{len(todo)}] ex={ex['ex_num']:<5} ERR: {e}"
                    logger.info(msg)
                    logger.info(tb)

        dt = time.time() - t0

        # Estimate cost
        price = PRICING.get(
            model,
            PRICING.get(
                "gpt-5"
                if "gpt-5" in model
                else ("gpt-4o-2024-08-06" if "gpt-4o" in model else ""),
                {"in": 0.0, "out": 0.0},
            ),
        )
        cost = (
            USAGE["prompt_tokens"] * price["in"] * 1e-6
            + USAGE["completion_tokens"] * price["out"] * 1e-6
        )

        logger.info(f"\nPredictions done in {dt / 60:.1f} min — ok={n_ok} err={n_err}")
        logger.info(f"LLM calls: {USAGE['calls']} | tool calls: {USAGE['tool_calls']}")
        logger.info(
            f"Tokens: in={USAGE['prompt_tokens']:,} out={USAGE['completion_tokens']:,} | est cost: ${cost:.4f}"
        )
        if n_graded:
            logger.info(
                f"Mean token F1 (new predictions): {f1_sum / n_graded:.4f} ({n_graded} graded)"
            )

    # Aggregate F1 over all completed predictions
    all_files = sorted(out_dir.glob("llm_qa_judgement__*.json"))
    if all_files:
        all_f1 = []
        all_em = []
        for p in all_files:
            rec = json.loads(p.read_text())
            if rec.get("token_f1") is not None:
                all_f1.append(rec["token_f1"])
            if rec.get("token_em") is not None:
                all_em.append(rec["token_em"])
        if all_f1:
            logger.info(f"\nAggregate over {len(all_f1)} examples:")
            logger.info(f"  Mean token F1: {sum(all_f1) / len(all_f1):.4f}")
            logger.info(f"  Mean token EM: {sum(all_em) / len(all_em):.4f}")

    # Optional: LLM judge grading
    if args.judge:
        logger.info(
            f"\nRunning LLM judge ({args.judge_model}) on {len(all_files)} predictions..."
        )
        judge_api_key = os.environ.get("OPENAI_API_KEY", "").strip() or api_key
        judge_base_url = os.environ.get(
            "OPENAI_BASE_URL", "https://api.openai.com/v1"
        ).strip()

        n_judged = n_skip_judge = n_judge_err = 0
        judge_f1_sum = 0.0

        def _judge_wrapper(p: Path) -> tuple[Path, dict | None, str]:
            rec = json.loads(p.read_text())
            if rec.get("judge_f1") is not None:
                return p, rec, "skip"
            try:
                scores = judge_one(rec, args.judge_model, judge_api_key, judge_base_url)
                rec.update(scores)
                tmp = p.with_suffix(p.suffix + ".tmp")
                tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=2))
                os.replace(tmp, p)
                return p, rec, "ok"
            except Exception as e:
                return p, None, f"err:{e}"

        with cf.ThreadPoolExecutor(max_workers=args.judge_workers) as pool:
            futs = [pool.submit(_judge_wrapper, p) for p in all_files]
            for i, fut in enumerate(cf.as_completed(futs), 1):
                path, rec, status = fut.result()
                if status == "ok":
                    n_judged += 1
                    jf1 = rec.get("judge_f1", 0.0)
                    judge_f1_sum += jf1
                    if i % 50 == 0 or i == len(futs):
                        logger.info(f"  Judged {i}/{len(futs)}")
                elif status == "skip":
                    n_skip_judge += 1
                    jf1 = rec.get("judge_f1", 0.0) if rec else 0.0
                    judge_f1_sum += jf1
                else:
                    n_judge_err += 1

        n_total_judge = n_judged + n_skip_judge
        if n_total_judge:
            logger.info(
                f"Judge: {n_judged} new + {n_skip_judge} cached = {n_total_judge} total ({n_judge_err} errors)"
            )
            logger.info(f"Mean judge F1: {judge_f1_sum / n_total_judge:.4f}")

    # Write aggregate summary
    summary_path = out_dir / "summary.json"
    summary: dict = {
        "tag": tag,
        "model": model,
        "retrieval": args.retrieval,
        "n_predictions": len(all_files),
    }
    if all_f1:
        summary["mean_token_f1"] = round(sum(all_f1) / len(all_f1), 4)
        summary["mean_token_em"] = round(sum(all_em) / len(all_em), 4)
    if args.judge and n_total_judge:
        summary["mean_judge_f1"] = round(judge_f1_sum / n_total_judge, 4)
    summary["usage"] = dict(USAGE)
    summary_path.write_text(json.dumps(summary, indent=2))
    logger.info(f"\nSummary written to {summary_path}")
