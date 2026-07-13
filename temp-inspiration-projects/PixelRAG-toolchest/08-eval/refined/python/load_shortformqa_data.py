def load_shortformqa_data(
    dataset_repo: str, num_examples: Optional[int] = None, shuffle: bool = False
) -> List[Dict]:
    """
    Load Short-form QA dataset data.

    Args:
        dataset_repo: HuggingFace dataset repository name
        num_examples: Limit to first N examples (optional)
        shuffle: Whether to shuffle the examples

    Returns:
        List of Short-form QA examples
    """
    dataset = datasets.load_dataset(dataset_repo, split="test")
    examples = []
    for example in dataset:
        example["problem"] = example["messages"][-1]["content"]
        example["id"] = hashlib.md5(example["problem"].encode()).hexdigest()
        example["answers"] = (
            json.loads(example["ground_truth"])
            if example["ground_truth"][0] == "["
            else [example["ground_truth"]]
        )
        example["additional_instructions"] = """
Your final response should be in the following format without any other text:
Exact Answer: <your succinct, final answer>
""".strip()
        examples.append(example)

    if shuffle:
        random.seed(42)
        random.shuffle(examples)

    if num_examples:
        examples = examples[:num_examples]

    return examples
