def load_simpleqa_references(path: Path, few_shot_count: int, seed: int) -> list[dict]:
    with path.open() as f:
        data = json.load(f)

    by_bucket = {}
    for item in data:
        question = item.get("question")
        answer = item.get("answer")
        if not isinstance(question, str) or not question.strip():
            continue
        bucket = question_start_bucket(question)
        by_bucket.setdefault(bucket, []).append(
            {
                "question": question.strip(),
                "answer": (answer or "").strip(),
                "topic": item.get("topic") or "Unknown",
            }
        )

    rng = random.Random(seed)
    for values in by_bucket.values():
        rng.shuffle(values)

    ordered_buckets = sorted(by_bucket, key=lambda key: (-len(by_bucket[key]), key))
    refs = []
    while len(refs) < few_shot_count and ordered_buckets:
        next_round = []
        for bucket in ordered_buckets:
            values = by_bucket[bucket]
            if values:
                refs.append(values.pop())
            if values:
                next_round.append(bucket)
            if len(refs) >= few_shot_count:
                break
        ordered_buckets = next_round
    return refs
