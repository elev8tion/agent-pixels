def load_factualvqa_data(
    num_examples: Optional[int] = None,
    shuffle: bool = False,
) -> List[Dict]:
    """
    Load FactualVQA dataset (lmms-lab/FVQA, train split).
    Factual VQA benchmark with search-required / search-free annotations.

    Columns: data_id, images (list of image dicts), prompt (list of message dicts),
             reward_model (dict with ground_truth), category (search_required/search_free).

    Returns:
        List of dicts with keys: id, problem, answer, image (PIL), additional_instructions, + metadata.
    """
    dataset = datasets.load_dataset("lmms-lab/FVQA", split="train")

    examples = []
    for sample in dataset:
        # Extract question from prompt[0]["content"]
        prompt_list = sample.get("prompt", [])
        if not prompt_list:
            continue
        question = prompt_list[0].get("content", "")
        if not question:
            continue

        # Extract answer from reward_model["ground_truth"]
        reward_model = sample.get("reward_model", {})
        if isinstance(reward_model, str):
            try:
                reward_model = json.loads(reward_model)
            except (json.JSONDecodeError, TypeError):
                reward_model = {}
        answer = reward_model.get("ground_truth", "")
        if not answer:
            continue

        # Extract first image
        pil_image = None
        images_list = sample.get("images", [])
        if images_list:
            pil_image = _bytes_to_pil(images_list[0])

        example = {
            "id": str(
                sample.get("data_id", hashlib.md5(question.encode()).hexdigest())
            ),
            "problem": question,
            "answer": answer,
            "image": pil_image,
            "additional_instructions": (
                "Your final response should be in the following format:\n"
                "Exact Answer: <your succinct, final answer>"
            ),
            # Metadata
            "category": sample.get("category", ""),
            "data_source": sample.get("data_source", ""),
        }
        examples.append(example)

    if shuffle:
        random.seed(42)
        random.shuffle(examples)

    if num_examples:
        examples = examples[:num_examples]

    return examples
