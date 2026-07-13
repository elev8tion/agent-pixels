def load_webqa_data(
    num_examples: Optional[int] = None,
    shuffle: bool = False,
) -> List[Dict]:
    """
    Load WebQA dataset (Anil99/webqa, validation split).
    Multimodal multi-hop reasoning benchmark where each question has text and/or image sources.

    NOTE: This dataset is large and may be slow to load. The HuggingFace viewer cannot
    render it due to row size (>1.4MB per row). We load the validation split and extract
    the question, answer, and image (if available) from the source snippets.

    If loading fails (e.g. dataset is gated, too large, or schema mismatch),
    this function logs a warning and returns an empty list.

    Returns:
        List of dicts with keys: id, problem, answer, image (PIL or None), additional_instructions.
    """
    try:
        # Use streaming to avoid memory issues with large rows (>1.4MB each)
        dataset = datasets.load_dataset(
            "Anil99/webqa", split="validation", streaming=True
        )
    except Exception as e:
        logger.warning(
            f"Failed to load WebQA dataset (Anil99/webqa): {e}. "
            "This dataset may require special handling due to its large row sizes. "
            "Returning empty list."
        )
        return []

    examples = []
    for idx, sample in enumerate(dataset):
        # WebQA structure varies; try common field names
        question = sample.get("question", sample.get("Q", ""))
        if not question:
            continue

        answer = sample.get("answer", sample.get("A", ""))
        if not answer:
            # Try extracting from Qcate or other fields
            answer = str(sample.get("answer", ""))

        # Try to extract an image from the sample
        pil_image = None
        # WebQA stores images in positive/negative fact lists; try to get one
        for img_key in ["img_posFacts", "img_pos", "image", "images"]:
            img_data = sample.get(img_key)
            if img_data is not None:
                if isinstance(img_data, list) and len(img_data) > 0:
                    first_item = img_data[0]
                    if isinstance(first_item, dict):
                        raw = first_item.get("image", first_item.get("bytes"))
                        if raw is not None:
                            pil_image = _bytes_to_pil(raw)
                    else:
                        pil_image = _bytes_to_pil(first_item)
                else:
                    pil_image = _bytes_to_pil(img_data)
                if pil_image is not None:
                    break

        example = {
            "id": str(sample.get("id", sample.get("guid", idx))),
            "problem": question,
            "answer": str(answer),
            "image": pil_image,
            "additional_instructions": (
                "Your final response should be in the following format:\n"
                "Exact Answer: <your succinct, final answer>"
            ),
            # Metadata
            "Qcate": sample.get("Qcate", ""),
        }
        examples.append(example)

        # With streaming, stop early once we have enough
        if num_examples and not shuffle and len(examples) >= num_examples:
            break

    if shuffle:
        random.seed(42)
        random.shuffle(examples)
        if num_examples:
            examples = examples[:num_examples]

    return examples
