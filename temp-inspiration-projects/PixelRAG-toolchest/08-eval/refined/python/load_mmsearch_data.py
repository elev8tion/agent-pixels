def load_mmsearch_data(
    num_examples: Optional[int] = None,
    shuffle: bool = False,
) -> List[Dict]:
    """
    Load MMSearch dataset (CaraJ/MMSearch, end2end config, 300 examples).
    Multimodal search benchmark with text queries, query images, and ground-truth answers.

    Columns: sample_id, query, query_image, image_search_result, area, subfield,
             timestamp, gt_requery, gt_answer, alternative_gt_answers.

    Returns:
        List of dicts with keys: id, problem, answer, image (PIL), additional_instructions, + metadata.
    """
    dataset = datasets.load_dataset("CaraJ/MMSearch", "end2end", split="end2end")

    examples = []
    for sample in dataset:
        pil_image = None
        raw_img = sample.get("query_image")
        if raw_img is not None:
            pil_image = _bytes_to_pil(raw_img)

        alt_answers = sample.get("alternative_gt_answers", [])
        if isinstance(alt_answers, str):
            try:
                alt_answers = json.loads(alt_answers)
            except (json.JSONDecodeError, TypeError):
                alt_answers = [alt_answers] if alt_answers else []

        gt_answer = sample.get("gt_answer", "")
        # Build combined answer string for evaluation: primary + alternatives
        all_answers = [gt_answer] + [a for a in alt_answers if a]
        answer_str = " | ".join(all_answers) if len(all_answers) > 1 else gt_answer

        example = {
            "id": str(sample.get("sample_id", "")),
            "problem": sample.get("query", ""),
            "answer": answer_str,
            "image": pil_image,
            "additional_instructions": (
                "Your final response should be in the following format:\n"
                "Exact Answer: <your succinct, final answer>"
            ),
            # Metadata
            "alternative_gt_answers": alt_answers,
            "gt_answer": gt_answer,
            "area": sample.get("area", ""),
            "subfield": sample.get("subfield", ""),
            "timestamp": sample.get("timestamp", ""),
            "gt_requery": sample.get("gt_requery", ""),
        }
        examples.append(example)

    if shuffle:
        random.seed(42)
        random.shuffle(examples)

    if num_examples:
        examples = examples[:num_examples]

    return examples
