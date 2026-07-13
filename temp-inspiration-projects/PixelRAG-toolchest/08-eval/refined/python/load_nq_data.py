def load_nq_data(
    num_examples: int | None = 1000, split: str = "validation"
) -> list[dict]:
    """Load Natural Questions (full) split.

    For validation, follows the short-answer protocol used by our NQ eval:
    keep only examples where >=2 of 5 annotators marked a non-null short
    answer. The train split has a single annotation per example, so train keeps
    examples with a non-null short answer.

    Source: HuggingFace google-research-datasets/natural_questions.
    Reference: Kwiatkowski et al. (2019).

    Args:
        num_examples: Number of examples to return. Default 1000.
        split: HuggingFace split to stream ("train" or "validation").

    Returns:
        List of dicts with id, problem, gold_answers, metadata.
    """
    from datasets import load_dataset
    import html as _html

    if split not in {"train", "validation"}:
        raise ValueError(
            f"Unsupported NQ split: {split!r}. Expected 'train' or 'validation'."
        )

    logger.info(f"Loading NQ {split} split (streaming)...")
    ds = load_dataset(
        "google-research-datasets/natural_questions",
        split=split,
        streaming=True,
    )

    data = []
    for ex in ds:
        # Extract short answers from all 5 annotators
        annotations = ex["annotations"]
        short_answer_texts = set()
        non_null_annotators = 0

        # annotations is a dict with list values (one per annotator)
        num_annotators = len(annotations["id"])
        for i in range(num_annotators):
            texts = annotations["short_answers"][i].get("text", [])
            if texts:
                non_null_annotators += 1
                for t in texts:
                    if t.strip():
                        short_answer_texts.add(t.strip())

        min_non_null = 2 if split == "validation" else 1
        if non_null_annotators < min_non_null:
            continue

        if not short_answer_texts:
            continue

        question_text = ex["question"]["text"]
        doc_url = ex["document"]["url"]
        # Clean up HTML entities in URL (e.g., &amp; -> &)
        doc_url = _html.unescape(doc_url)
        # Normalize NQ URL format: /w/index.php?title=Foo&oldid=123 -> /wiki/Foo
        _title_match = re.search(r"[?&]title=([^&]+)", doc_url)
        if _title_match:
            doc_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(_title_match.group(1), safe='/:(),-')}"

        example = {
            "id": hashlib.md5(question_text.encode()).hexdigest(),
            "problem": question_text,
            "gold_answers": sorted(short_answer_texts),
            "metadata": {
                "urls": [doc_url],
                "dataset": "nq",
                "document_title": ex["document"]["title"],
            },
        }
        data.append(example)

        if num_examples and len(data) >= num_examples:
            break

    filter_desc = (
        ">=2 annotator agreement" if split == "validation" else "non-null short answer"
    )
    logger.info(f"Loaded {len(data)} NQ {split} examples (filtered by {filter_desc}).")
    return data
