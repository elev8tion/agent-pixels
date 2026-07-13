def load_piqa_data(num_examples: int | None = None) -> list[dict]:
    """Load PIQA (Physical Intuition QA) validation split.

    2-choice physical commonsense benchmark. Label is 0 or 1.
    Source: HuggingFace `ybisk/piqa`, validation split.

    Returns list of dicts with problem (question only), gold_answers (letter),
    additional_instructions (options + MC instruction), metadata.
    """
    from datasets import load_dataset

    logger.info("Loading PIQA validation split...")
    ds = load_dataset("ybisk/piqa", split="validation", revision="refs/convert/parquet")

    data = []
    for ex in ds:
        question = ex["goal"]
        options = [ex["sol1"], ex["sol2"]]
        label = int(ex["label"])
        gold_letter = LETTERS[label]

        options_text = _format_mc_options(LETTERS[:2], options)
        example = {
            "id": hashlib.md5(question.encode()).hexdigest(),
            "problem": question,
            "gold_answers": [gold_letter],
            "additional_instructions": f"{options_text}\n\n{MC_INSTRUCTION}",
            "metadata": {"dataset": "piqa", "urls": [], "gold_letter": gold_letter},
        }
        data.append(example)
        if num_examples and len(data) >= num_examples:
            break

    logger.info(f"Loaded {len(data)} PIQA examples.")
    return data
