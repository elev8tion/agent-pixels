def load_triviaqa_data(num_examples: int | None = 1000) -> list[dict]:
    """Load TriviaQA rc.wikipedia validation split.

    Uses entity_pages.title to construct ground truth Wikipedia URLs.
    gold_answers includes answer.value + answer.aliases (following TriviaQA official eval).

    Source: HuggingFace mandarjoshi/trivia_qa, config rc.wikipedia, validation split.
    Reference: Joshi et al. (2017).

    Args:
        num_examples: Number of examples to return. Default 1000.

    Returns:
        List of dicts with id, problem, gold_answers, metadata.
    """
    from datasets import load_dataset
    import ast as _ast
    from urllib.parse import quote as _url_quote

    logger.info("Loading TriviaQA rc.wikipedia validation split (streaming)...")
    ds = load_dataset(
        "mandarjoshi/trivia_qa",
        "rc.wikipedia",
        split="validation",
        streaming=True,
    )

    data = []
    for ex in ds:
        question = ex["question"]
        answer_obj = ex["answer"]

        # Extract gold answers: value + aliases
        gold_answers = set()
        value = answer_obj.get("value", "")
        if value:
            gold_answers.add(value)

        # aliases is stored as a string repr of a list
        aliases_raw = answer_obj.get("aliases", "")
        if isinstance(aliases_raw, str) and aliases_raw:
            try:
                aliases = _ast.literal_eval(aliases_raw)
                if isinstance(aliases, list):
                    for a in aliases:
                        if a and a.strip():
                            gold_answers.add(a.strip())
            except (ValueError, SyntaxError):
                pass
        elif isinstance(aliases_raw, list):
            for a in aliases_raw:
                if a and a.strip():
                    gold_answers.add(a.strip())

        if not gold_answers:
            continue

        # Construct Wikipedia URL from entity_pages.title
        urls = []
        entity_titles = ex.get("entity_pages", {}).get("title", [])
        if entity_titles:
            for title in entity_titles:
                if title:
                    wiki_url = f"https://en.wikipedia.org/wiki/{_url_quote(title.replace(' ', '_'))}"
                    urls.append(wiki_url)

        example = {
            "id": hashlib.md5(question.encode()).hexdigest(),
            "problem": question,
            "gold_answers": sorted(gold_answers),
            "question_type": ex.get("question_source", ""),
            "metadata": {
                "urls": urls,
                "dataset": "triviaqa",
                "question_id": ex.get("question_id", ""),
            },
        }
        data.append(example)

        if num_examples and len(data) >= num_examples:
            break

    logger.info(f"Loaded {len(data)} TriviaQA examples.")
    return data
