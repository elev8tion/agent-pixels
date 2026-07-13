def load_arc_data(
    config: str = "ARC-Challenge", num_examples: int | None = None
) -> list[dict]:
    """Load ARC (AI2 Reasoning Challenge) test split.

    3-5 choice science exam benchmark. answerKey is A-E or 1-5 (normalized to letters).
    Source: HuggingFace `allenai/ai2_arc`, ARC-Challenge or ARC-Easy config, test split.

    Args:
        config: "ARC-Challenge" or "ARC-Easy"
        num_examples: Max examples to return. None = all.
    """
    from datasets import load_dataset

    dataset_name = config.lower().replace("-", "_")
    logger.info(f"Loading ARC {config} test split...")
    ds = load_dataset("allenai/ai2_arc", config, split="test")

    # ARC answerKey can be "1","2","3","4","5" instead of letters
    DIGIT_TO_LETTER = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "E"}

    data = []
    for ex in ds:
        question = ex["question"]
        labels = ex["choices"]["label"]
        texts = ex["choices"]["text"]
        gold_letter = ex["answerKey"]
        gold_letter = DIGIT_TO_LETTER.get(gold_letter, gold_letter)

        options_text = _format_mc_options(labels, texts)
        example = {
            "id": hashlib.md5(question.encode()).hexdigest(),
            "problem": question,
            "gold_answers": [gold_letter],
            "additional_instructions": f"{options_text}\n\n{MC_INSTRUCTION}",
            "metadata": {
                "dataset": dataset_name,
                "urls": [],
                "gold_letter": gold_letter,
            },
        }
        data.append(example)
        if num_examples and len(data) >= num_examples:
            break

    logger.info(f"Loaded {len(data)} ARC {config} examples.")
    return data
