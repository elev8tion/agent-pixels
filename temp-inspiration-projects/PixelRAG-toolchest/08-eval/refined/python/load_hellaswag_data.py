def load_hellaswag_data(num_examples: int | None = None) -> list[dict]:
    """Load HellaSwag validation split.

    4-choice sentence completion benchmark. Label is "0"-"3".
    Source: HuggingFace `Rowan/hellaswag`, validation split.
    """
    from datasets import load_dataset

    logger.info("Loading HellaSwag validation split...")
    ds = load_dataset(
        "Rowan/hellaswag", split="validation", revision="refs/convert/parquet"
    )

    data = []
    for ex in ds:
        question = ex["ctx"]
        options = ex["endings"]
        label = int(ex["label"])
        gold_letter = LETTERS[label]

        options_text = _format_mc_options(LETTERS[: len(options)], options)
        example = {
            "id": hashlib.md5(question.encode()).hexdigest(),
            "problem": question,
            "gold_answers": [gold_letter],
            "additional_instructions": f"{options_text}\n\n{MC_INSTRUCTION}",
            "metadata": {
                "dataset": "hellaswag",
                "urls": [],
                "gold_letter": gold_letter,
            },
        }
        data.append(example)
        if num_examples and len(data) >= num_examples:
            break

    logger.info(f"Loaded {len(data)} HellaSwag examples.")
    return data
