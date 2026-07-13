def load_simpleqa_by_domain(domain: str, num_examples: int | None = None) -> list[dict]:
    """Load SimpleQA examples filtered by URL domain.

    Args:
        domain: Domain to filter by (e.g., 'wikipedia', 'arxiv', 'github').
        num_examples: Number of examples to return.

    Returns:
        List of examples where at least one URL contains the domain.
    """
    all_data = load_simpleqa_data(num_examples=None)

    filtered = []
    for example in all_data:
        urls = _get_urls_from_metadata(example)
        if any(domain.lower() in url.lower() for url in urls):
            filtered.append(example)

    logger.info(f"Found {len(filtered)} examples with '{domain}' URLs")

    if num_examples:
        filtered = filtered[:num_examples]
        logger.info(f"Limiting to first {num_examples} examples")

    return filtered
