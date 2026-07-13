def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-VL-Embedding-2B")
    parser.add_argument(
        "--adapter", type=str, required=True, help="Path to LoRA adapter dir"
    )
    parser.add_argument("--eval-jsonl", default="training/data/eval.jsonl")
    parser.add_argument("--max-pairs", type=int, default=100)
    parser.add_argument("--max-visual-tokens", type=int, default=1024)
    args = parser.parse_args()

    # Load eval data
    pairs = []
    with open(args.eval_jsonl) as f:
        for line in f:
            item = json.loads(line)
            try:
                img = Image.open(item["chunk_path"]).convert("RGB")
                pairs.append((item["query"], img))
            except Exception:
                continue
    pairs = pairs[: args.max_pairs]
    queries = [p[0] for p in pairs]
    images = [p[1] for p in pairs]
    logger.info(f"Loaded {len(pairs)} eval pairs")

    results = {}

    # 1. Base model (no LoRA)
    logger.info("=== Base model (no fine-tuning) ===")
    model, processor = load_model_and_processor(
        args.model, adapter_path=None, max_visual_tokens=args.max_visual_tokens
    )
    q_embs = embed_queries(model, processor, queries)
    i_embs = embed_images(model, processor, images)
    base_metrics = compute_metrics(q_embs, i_embs)
    results["base"] = base_metrics
    for k, v in base_metrics.items():
        logger.info(f"  {k}: {v:.4f}")
    del model
    torch.cuda.empty_cache()

    # 2. Fine-tuned model (with LoRA)
    logger.info(f"=== Fine-tuned model ({args.adapter}) ===")
    model, processor = load_model_and_processor(
        args.model, adapter_path=args.adapter, max_visual_tokens=args.max_visual_tokens
    )
    q_embs_ft = embed_queries(model, processor, queries)
    i_embs_ft = embed_images(model, processor, images)
    ft_metrics = compute_metrics(q_embs_ft, i_embs_ft)
    results["finetuned"] = ft_metrics
    for k, v in ft_metrics.items():
        logger.info(f"  {k}: {v:.4f}")
    del model
    torch.cuda.empty_cache()

    # 3. Comparison
    logger.info("=== Comparison ===")
    for k in base_metrics:
        diff = ft_metrics[k] - base_metrics[k]
        arrow = "↑" if diff > 0 else "↓" if diff < 0 else "="
        logger.info(
            f"  {k}: {base_metrics[k]:.4f} → {ft_metrics[k]:.4f} ({arrow}{abs(diff):.4f})"
        )
