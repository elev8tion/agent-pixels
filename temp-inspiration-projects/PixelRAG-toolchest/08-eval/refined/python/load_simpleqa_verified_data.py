def load_simpleqa_verified_data(num_examples: int | None = None) -> list[dict]:
    """Load SimpleQA Verified dataset from Hugging Face.

    Args:
        num_examples: Optional limit on number of examples to load.

    Returns:
        List of example dictionaries with 'id', 'problem', 'answer', etc.
        Compatible format with SimpleQA dataset.
    """
    logger.info("Loading SimpleQA Verified dataset...")
    try:
        # Try using datasets library first (recommended)
        try:
            from datasets import load_dataset

            logger.info("Using Hugging Face datasets library...")
            dataset = load_dataset("google/simpleqa-verified", split="eval")
            df = dataset.to_pandas()
        except ImportError:
            logger.warning("datasets library not available, trying alternative methods")
            # Fallback: try Hugging Face datasets-server API
            try:
                import requests

                logger.info("Trying Hugging Face datasets-server API...")
                api_url = "https://datasets-server.huggingface.co/parquet?dataset=google%2Fsimpleqa-verified&config=simpleqa_verified&split=eval"
                response = requests.get(api_url, timeout=60)
                if response.status_code == 200:
                    import io

                    df = pd.read_parquet(io.BytesIO(response.content))
                    logger.info("Successfully loaded via datasets-server API")
                else:
                    raise Exception(
                        f"Failed to download dataset: HTTP {response.status_code}"
                    )
            except Exception as e:
                logger.error(f"Failed to load via API: {e}")
                # Last resort: try direct file download
                try:
                    logger.info("Trying direct file download...")
                    # Try parquet file
                    parquet_url = "https://huggingface.co/datasets/google/simpleqa-verified/resolve/main/data/eval-00000-of-00001.parquet"
                    df = pd.read_parquet(parquet_url)
                    logger.info("Successfully loaded via direct file download")
                except Exception as e2:
                    logger.error(f"Failed to load via direct download: {e2}")
                    raise Exception(
                        "All methods failed. Please install 'datasets' library: pip install datasets"
                    )
    except Exception as e:
        logger.error(f"Failed to load SimpleQA Verified dataset: {e}")
        raise

    # Ensure stable ordering: reset index to maintain original order
    df = df.reset_index(drop=True)

    # Convert to compatible format with SimpleQA
    # SimpleQA Verified has: original_index, problem, answer, topic, answer_type, multi_step, requires_reasoning, urls
    # SimpleQA has: metadata (with urls), problem, answer, id

    # Generate unique ID from problem text (same as SimpleQA)
    df["id"] = df["problem"].apply(
        lambda problem: hashlib.md5(problem.encode()).hexdigest()
    )

    # Convert urls to list format if it's a string
    def normalize_urls(urls):
        """Normalize URLs to list format."""
        if isinstance(urls, str):
            # Try to parse as list string
            try:
                import ast

                return ast.literal_eval(urls)
            except Exception:
                # Split by comma if it's a comma-separated string
                return [u.strip() for u in urls.split(",") if u.strip()]
        elif isinstance(urls, list):
            return urls
        else:
            return []

    # Normalize URLs column
    if "urls" in df.columns:
        df["urls"] = df["urls"].apply(normalize_urls)
    else:
        df["urls"] = [[]] * len(df)

    # Convert to metadata format compatible with SimpleQA
    def create_metadata(row):
        """Create metadata dict compatible with SimpleQA format."""
        metadata = {
            "topic": str(row.get("topic", "")),
            "answer_type": str(row.get("answer_type", "")),
            "urls": row.get("urls", []),
        }
        if "multi_step" in row and pd.notna(row["multi_step"]):
            metadata["multi_step"] = bool(row["multi_step"])
        if "requires_reasoning" in row and pd.notna(row["requires_reasoning"]):
            metadata["requires_reasoning"] = bool(row["requires_reasoning"])
        if "original_index" in row and pd.notna(row["original_index"]):
            metadata["original_index"] = int(row["original_index"])
        # Convert to string format similar to SimpleQA (using single quotes for Python dict string)
        return str(metadata)

    df["metadata"] = df.apply(create_metadata, axis=1)

    # Convert to list of dicts, maintaining original order
    data = [row.to_dict() for _, row in df.iterrows()]

    if num_examples:
        logger.info(f"Limiting to first {num_examples} examples.")
        data = data[:num_examples]

    logger.info(f"Loaded {len(data)} SimpleQA Verified examples.")
    return data
