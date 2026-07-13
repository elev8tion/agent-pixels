def load_simplevqa_data(
    num_examples: Optional[int] = None,
    shuffle: bool = False,
) -> List[Dict]:
    """
    Load SimpleVQA dataset (m-a-p/SimpleVQA, test split, ~2030 examples).
    Multi-modal factual VQA benchmark with images.

    Columns: data_id, image, image_description, language, question, answer,
             original_category, source, atomic_question, atomic_fact, vqa_category.

    Filters out Chinese-language examples by default.

    Returns:
        List of dicts with keys: id, problem, answer, image (PIL), additional_instructions, + metadata.
    """
    dataset = datasets.load_dataset("m-a-p/SimpleVQA", split="test")

    examples = []
    for sample in dataset:
        lang = sample.get("language", "")
        # Filter out Chinese examples
        if lang and lang.lower() in ("chinese", "zh", "cn"):
            continue

        pil_image = None
        raw_img = sample.get("image")
        if raw_img is not None:
            pil_image = _bytes_to_pil(raw_img)

        example = {
            "id": str(sample["data_id"]),
            "problem": sample["question"],
            "answer": sample["answer"],
            "image": pil_image,
            "additional_instructions": (
                "Your final response should be in the following format:\n"
                "Exact Answer: <your succinct, final answer>"
            ),
            # Metadata
            "language": lang,
            "original_category": sample.get("original_category", ""),
            "vqa_category": sample.get("vqa_category", ""),
            "source": sample.get("source", ""),
        }
        examples.append(example)

    if shuffle:
        random.seed(42)
        random.shuffle(examples)

    if num_examples:
        examples = examples[:num_examples]

    return examples
