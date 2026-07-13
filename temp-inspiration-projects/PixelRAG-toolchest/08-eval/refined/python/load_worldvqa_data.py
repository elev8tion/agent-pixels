def load_worldvqa_data(
    num_examples: Optional[int] = None,
    shuffle: bool = False,
    language_filter: Optional[str] = None,
) -> List[Dict]:
    """
    Load WorldVQA dataset from HuggingFace.

    Args:
        num_examples: Limit to first N examples (optional)
        shuffle: Whether to shuffle the examples

    Returns:
        List of WorldVQA examples
    """
    dataset = datasets.load_dataset("moonshotai/WorldVQA", split="train")

    examples = []
    for idx, sample in enumerate(dataset):
        lang = sample.get("language", "")
        # Filter out Chinese examples by default
        if lang == "zh":
            continue

        example = {
            "id": str(idx),
            "problem": sample["question"],
            "answer": sample["answer"],
            "additional_instructions": (
                "Your final response should be in the following format:\n"
                "Exact Answer: <your succinct, final answer>"
            ),
        }
        # Preserve metadata
        for col in ["image", "category", "difficulty", "language"]:
            if col in sample:
                example[col] = sample[col]

        examples.append(example)

    if language_filter:
        examples = [ex for ex in examples if ex.get("language") == language_filter]

    if shuffle:
        random.seed(42)
        random.shuffle(examples)

    if num_examples:
        examples = examples[:num_examples]

    return examples
