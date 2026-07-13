def select_rows(
    rows: list[dict], reviews: dict[int, dict], args: argparse.Namespace
) -> list[dict]:
    candidates = []
    for row in rows:
        review = reviews.get(row["row_id"])
        if not review:
            continue
        direct_keep = (
            review["keep"]
            and review["naturalness"] >= args.min_naturalness
            and review["simpleqa_style_fit"] >= args.min_style_fit
        )
        if direct_keep:
            candidates.append((row, review))

    if args.dedupe_query:
        by_query = {}
        for row, review in candidates:
            key = normalize_query(row["query"])
            current = by_query.get(key)
            if current is None or candidate_priority(review) > candidate_priority(
                current[1]
            ):
                by_query[key] = (row, review)
        candidates = list(by_query.values())

    candidates.sort(key=lambda item: candidate_priority(item[1]), reverse=True)

    if args.target_count > 0 and len(candidates) > args.target_count:
        candidates = candidates[: args.target_count]

    return [row for row, _ in candidates]
