def load_retrieval_queries(jsonl_path, max_examples=0):
    """Load query -> gold image pairs for retrieval eval against the full datastore."""
    examples = []
    with open(jsonl_path) as f:
        for line in f:
            item = json.loads(line)
            chunk_path = resolve_jsonl_path(jsonl_path, item["chunk_path"])
            examples.append(
                {
                    "query": item["query"],
                    "gold_path": chunk_path,
                }
            )
            if max_examples > 0 and len(examples) >= max_examples:
                break
    logger.info(f"Loaded {len(examples)} retrieval queries from {jsonl_path}")
    return examples
