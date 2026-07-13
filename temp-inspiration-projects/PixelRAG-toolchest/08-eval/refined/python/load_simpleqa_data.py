def load_simpleqa_data(num_examples: int | None = None) -> list[dict]:
    """Load SimpleQA dataset.

    Args:
        num_examples: Optional limit on number of examples to load.

    Returns:
        List of example dictionaries with 'id', 'problem', 'answer', etc.
    """
    logger.info("Loading SimpleQA dataset...")
    try:
        local_path = "evaluation/simple_qa_eval/data/simple_qa_test_set.csv"
        if os.path.exists(local_path):
            df = pd.read_csv(local_path)
        else:
            url = "https://openaipublic.blob.core.windows.net/simple-evals/simple_qa_test_set.csv"
            df = pd.read_csv(url)
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        url = "https://openaipublic.blob.core.windows.net/simple-evals/simple_qa_test_set.csv"
        df = pd.read_csv(url)

    # Ensure stable ordering: reset index to maintain original CSV row order
    df = df.reset_index(drop=True)

    # Generate unique ID from problem text
    df["id"] = df["problem"].apply(
        lambda problem: hashlib.md5(problem.encode()).hexdigest()
    )

    # Convert to list of dicts, maintaining original CSV order
    data = [row.to_dict() for _, row in df.iterrows()]

    if num_examples:
        logger.info(f"Limiting to first {num_examples} examples.")
        data = data[:num_examples]

    logger.info(f"Loaded {len(data)} examples.")
    return data
