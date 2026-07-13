def load_multimodalqa_data(
    num_examples: Optional[int] = None,
    shuffle: bool = False,
) -> List[Dict]:
    """
    Load MultiModalQA dataset (allenai/multimodalqa).
    Cross-modal QA benchmark requiring reasoning over text, tables, and images.

    NOTE: This dataset is hosted on GitHub (not HuggingFace). Images require a
    separate 3.6GB download from S3 (images.zip). This loader attempts to load
    the dev split questions from HuggingFace (community mirror) or falls back to
    downloading from the official GitHub release. Images are NOT loaded automatically;
    the `image` field will be None unless the images are pre-downloaded to
    ~/.cache/dr_agent/datasets/multimodalqa_images/.

    If no HuggingFace mirror is available, we download the dev JSONL directly from GitHub.

    Returns:
        List of dicts with keys: id, problem, answer, image (PIL or None), additional_instructions, + metadata.
    """
    import gzip

    cache_dir = get_cache_dir()
    dev_jsonl_path = cache_dir / "MultiModalQA_dev.jsonl"

    # Try loading from HuggingFace mirror first, fall back to GitHub raw files
    questions = []
    try:
        # Try the official GitHub raw file
        if not dev_jsonl_path.exists():
            dev_gz_url = "https://raw.githubusercontent.com/allenai/multimodalqa/master/dataset/MMQA_dev.jsonl.gz"
            gz_path = cache_dir / "MultiModalQA_dev.jsonl.gz"
            logger.info("Downloading MultiModalQA dev set from GitHub...")
            urllib.request.urlretrieve(dev_gz_url, gz_path)
            with gzip.open(gz_path, "rt", encoding="utf-8") as f_in:
                with open(dev_jsonl_path, "w", encoding="utf-8") as f_out:
                    f_out.write(f_in.read())
            gz_path.unlink(missing_ok=True)

        with open(dev_jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    questions.append(json.loads(line))
    except Exception as e:
        logger.warning(
            f"Failed to load MultiModalQA dataset: {e}. "
            "The dataset requires downloading from GitHub "
            "(https://github.com/allenai/multimodalqa). Returning empty list."
        )
        return []

    if not questions:
        logger.warning("MultiModalQA dev set is empty after loading.")
        return []

    # Check if images directory exists for optional image loading
    # Images may be in multimodalqa_images/ or multimodalqa_images/final_dataset_images/
    images_dir = cache_dir / "multimodalqa_images" / "final_dataset_images"
    if not images_dir.is_dir():
        images_dir = cache_dir / "multimodalqa_images"
    has_images = images_dir.is_dir()
    if not has_images:
        logger.info(
            "MultiModalQA images not found at %s. Image field will be None. "
            "To enable images, download and extract: "
            "https://multimodalqa-images.s3-us-west-2.amazonaws.com/final_dataset_images/final_dataset_images.zip "
            "into %s",
            images_dir,
            images_dir,
        )

    examples = []
    for sample in questions:
        qid = sample.get("qid", "")
        question_text = sample.get("question", "")
        if not question_text:
            continue

        # Extract answers (list of answer dicts)
        answers_raw = sample.get("answers", [])
        if isinstance(answers_raw, list):
            answer_texts = []
            for ans in answers_raw:
                if isinstance(ans, dict):
                    answer_texts.append(ans.get("answer", ""))
                elif isinstance(ans, str):
                    answer_texts.append(ans)
            answer_str = " | ".join(str(a) for a in answer_texts if a) or ""
        elif isinstance(answers_raw, str):
            answer_str = answers_raw
        else:
            answer_str = str(answers_raw)

        # Try to load image if images are downloaded
        pil_image = None
        if has_images:
            # MultiModalQA references images via metadata.image_doc_ids
            metadata = sample.get("metadata", {})
            image_doc_ids = metadata.get("image_doc_ids", [])
            for img_id in image_doc_ids:
                # Images are stored as {img_id}.jpg or {img_id}.png
                for ext in (".jpg", ".jpeg", ".png"):
                    img_path = images_dir / f"{img_id}{ext}"
                    if img_path.exists():
                        try:
                            pil_image = Image.open(img_path).convert("RGB")
                        except Exception:
                            pass
                        break
                if pil_image is not None:
                    break

        # Extract modality info
        metadata = sample.get("metadata", {})
        example = {
            "id": str(qid),
            "problem": question_text,
            "answer": answer_str,
            "image": pil_image,
            "additional_instructions": (
                "Your final response should be in the following format:\n"
                "Exact Answer: <your succinct, final answer>"
            ),
            # Metadata
            "reasoning_type": metadata.get("type", ""),
            "modalities": metadata.get("modalities", []),
        }
        examples.append(example)

    if shuffle:
        random.seed(42)
        random.shuffle(examples)

    if num_examples:
        examples = examples[:num_examples]

    return examples
