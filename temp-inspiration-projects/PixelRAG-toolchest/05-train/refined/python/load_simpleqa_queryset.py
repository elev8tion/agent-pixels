def load_simpleqa_queryset(jsonl_path=None, max_examples=1000, articles_json=None):
    """Load SimpleQA queryset JSONL bundled with this repo."""
    examples = []
    slug_to_aid = None
    if jsonl_path and os.path.exists(jsonl_path):
        with open(jsonl_path) as f:
            for line in f:
                item = json.loads(line)
                gold_article_ids = list(item.get("gold_article_ids", []))
                if not gold_article_ids and articles_json:
                    if slug_to_aid is None:
                        slug_to_aid = load_slug_to_article_id(articles_json)
                    seen = set()
                    for url in item.get("urls", []):
                        slug = wikipedia_url_to_slug(url)
                        aid = slug_to_aid.get(slug) if slug else None
                        if aid is not None and aid not in seen:
                            seen.add(aid)
                            gold_article_ids.append(aid)
                examples.append(
                    {
                        "id": item.get("id", str(len(examples))),
                        "query": item.get("query", item.get("problem", "")),
                        "answer": item.get("answer", ""),
                        "urls": item.get("urls", []),
                        "gold_article_ids": gold_article_ids,
                    }
                )
                if max_examples > 0 and len(examples) >= max_examples:
                    break
        logger.info(f"Loaded {len(examples)} SimpleQA queries from {jsonl_path}")
        return examples

    raise FileNotFoundError(f"SimpleQA queryset not found at {jsonl_path!r}.")
