def load_encyclopedic_vqa_data(
    split: str = "val",
    num_examples: Optional[int] = None,
    shuffle: bool = False,
    local_path: Optional[str] = None,
    dataset_filter: Optional[str] = None,
    question_type_filter: Optional[str] = None,
) -> List[Dict]:
    """
    Load Encyclopedic VQA dataset.

    Args:
        split: Dataset split ('val' or 'test')
        num_examples: Limit to first N examples (optional)
        shuffle: Whether to shuffle the examples
        local_path: Optional local path to dataset CSV
        dataset_filter: Filter by dataset_name ('inaturalist' or 'landmarks')
        question_type_filter: Filter by question_type ('templated', 'automatic', 'multi_answer', '2_hop')

    Returns:
        List of Encyclopedic VQA examples
    """
    if local_path and Path(local_path).exists():
        df = pd.read_csv(local_path)
    else:
        url_key = f"encyclopedic_vqa_{split}"
        cache_name = f"encyclopedic_vqa_{split}.csv"
        cache_path = download_file(DATASET_URLS[url_key], cache_name)
        df = pd.read_csv(cache_path)

    examples = []
    for idx, row in df.iterrows():
        question = str(row.get("question", ""))
        answer_raw = str(row.get("answer", ""))
        # Answers are pipe-separated
        reference_list = [a.strip() for a in answer_raw.split("|") if a.strip()]

        # Use question + wikipedia_url + row index for ID to avoid collisions
        # (templated questions repeat across species, and same species can have multiple image sets)
        wiki_url = str(row.get("wikipedia_url", ""))
        id_source = f"{question}|{wiki_url}|{idx}"
        example = {
            "id": hashlib.md5(id_source.encode()).hexdigest(),
            "problem": question,
            "answer": answer_raw,
            "reference_list": reference_list,
            "question_type": str(row.get("question_type", "automatic")),
            "additional_instructions": (
                "Your final response should be in the following format:\n"
                "Exact Answer: <your succinct, final answer>"
            ),
        }
        # Preserve optional metadata columns
        for col in [
            "wikipedia_url",
            "wikipedia_title",
            "question_original",
            "dataset_image_ids",
            "dataset_name",
            "wikipedia_url_used_in_train",
        ]:
            if col in row.index and pd.notna(row[col]):
                example[col] = row[col]

        # Map wikipedia_url into metadata so screenshot/retrieval pipeline can find it
        if "wikipedia_url" in example and example["wikipedia_url"]:
            example["metadata"] = {"url": example["wikipedia_url"]}

        # Parse dataset_image_ids for query images (iNaturalist or Google Landmarks)
        if "dataset_image_ids" in example and example["dataset_image_ids"]:
            raw_ids = str(example["dataset_image_ids"])
            ids = [i.strip() for i in raw_ids.split("|") if i.strip()]
            example["dataset_image_ids_parsed"] = ids
            if example.get("dataset_name", "").lower() == "inaturalist":
                example["inat_image_ids"] = ids  # backward compat

        examples.append(example)

    if dataset_filter:
        ds_lower = dataset_filter.lower()
        examples = [
            e for e in examples if (e.get("dataset_name") or "").lower() == ds_lower
        ]

    if question_type_filter:
        allowed_qts = frozenset(
            q.strip().lower() for q in question_type_filter.split(",") if q.strip()
        )
        examples = [
            e for e in examples if (e.get("question_type") or "").lower() in allowed_qts
        ]

    # Skip landmark examples with 404 query image URLs
    if dataset_filter and (dataset_filter.lower() == "landmarks"):

        def _has_404_only(e):
            ids = e.get("dataset_image_ids_parsed") or []
            return ids and set(ids) == {EVQA_LANDMARK_404_IMG_ID}

        examples = [
            e
            for e in examples
            if e.get("id") not in EVQA_LANDMARK_SKIP_IDS and not _has_404_only(e)
        ]

    if shuffle:
        random.seed(42)
        random.shuffle(examples)

    if num_examples:
        examples = examples[:num_examples]

    return examples
