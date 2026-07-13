def load_openbookqa_data(num_examples: int | None = None) -> list[dict]:
    """Load OpenBookQA test split.

    4-choice science QA benchmark. answerKey is A-D.
    Source: HuggingFace `allenai/openbookqa`, main config, test split.
    """
    from datasets import load_dataset

    logger.info("Loading OpenBookQA test split...")
    ds = load_dataset("allenai/openbookqa", "main", split="test")

    data = []
    for ex in ds:
        question = ex["question_stem"]
        labels = ex["choices"]["label"]
        texts = ex["choices"]["text"]
        gold_letter = ex["answerKey"]

        options_text = _format_mc_options(labels, texts)
        example = {
            "id": hashlib.md5(question.encode()).hexdigest(),
            "problem": question,
            "gold_answers": [gold_letter],
            "additional_instructions": f"{options_text}\n\n{MC_INSTRUCTION}",
            "metadata": {
                "dataset": "openbookqa",
                "urls": [],
                "gold_letter": gold_letter,
            },
        }
        data.append(example)
        if num_examples and len(data) >= num_examples:
            break

    logger.info(f"Loaded {len(data)} OpenBookQA examples.")
    return data
