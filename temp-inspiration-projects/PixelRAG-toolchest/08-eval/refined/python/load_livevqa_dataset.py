def load_livevqa_dataset(v4_path: str, max_samples: int | None = None) -> list[dict]:
    """Load LiveVQA QA pairs from the v4 JSON.

    Each row has: question, img_path, corpus_url, source, level, options,
    ground_truth (letter A-E), gt_hex_id, retrieved_hex_ids.
    """
    logger.info("Loading LiveVQA from %s", v4_path)
    with open(v4_path) as f:
        data = json.load(f)
    rows = data["per_query"]
    logger.info("Loaded %d QA pairs", len(rows))
    if max_samples:
        rows = rows[:max_samples]
        logger.info("Limited to %d samples", max_samples)
    return rows
