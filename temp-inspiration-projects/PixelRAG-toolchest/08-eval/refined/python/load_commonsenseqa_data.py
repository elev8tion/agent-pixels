def load_commonsenseqa_data(num_examples: int | None = None) -> list[dict]:
    """Load CommonsenseQA validation split.

    5-choice commonsense reasoning benchmark. answerKey is A-E.
    Source: HuggingFace `tau/commonsense_qa`, validation split.
    """
    from datasets import load_dataset

    logger.info("Loading CommonsenseQA validation split...")
    ds = load_dataset("tau/commonsense_qa", split="validation")

    data = []
    for ex in ds:
        question = ex["question"]
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
                "dataset": "commonsense_qa",
                "urls": [],
                "gold_letter": gold_letter,
            },
        }
        data.append(example)
        if num_examples and len(data) >= num_examples:
            break

    logger.info(f"Loaded {len(data)} CommonsenseQA examples.")
    return data
