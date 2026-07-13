def process_example(
    example_index: int, item: dict, args: argparse.Namespace, client_ctx: dict
) -> dict:
    query = item["query"]
    selected_hns = []
    review_rows = []
    counts = init_counts()

    positive_passage = item["passage"]
    positive_answer = None
    try:
        positive_answer = answer_question(
            client_ctx, args.model, query, positive_passage, args.max_retries
        )
        time.sleep(args.sleep_seconds)
        if normalize_answer(positive_answer) == "CANNOT_ANSWER":
            positive_verdict = "CANNOT_ANSWER"
        else:
            positive_verdict = judge_answer(
                client_ctx,
                args.model,
                query,
                positive_passage,
                positive_answer,
                args.max_retries,
            )
            time.sleep(args.sleep_seconds)
    except ApiRequestError as exc:
        counts["skip_reasons"]["api_error"] += 1
        review_rows.append(
            {
                "example_index": example_index,
                "query": query,
                "candidate_rank": None,
                "candidate_article_id": item["article_id"],
                "candidate_chunk_index": item["chunk_index"],
                "candidate_score": item.get("positive_score"),
                "candidate_title": item.get("title_guess"),
                "candidate_url": None,
                "answer": positive_answer,
                "verdict": "API_ERROR",
                "path_role": "positive",
                "skip_reason": "api_error",
                "error": str(exc),
            }
        )
        return {
            "kept_row": None,
            "review_rows": review_rows,
            "counts": counts,
        }

    review_rows.append(
        {
            "example_index": example_index,
            "query": query,
            "candidate_rank": None,
            "candidate_article_id": item["article_id"],
            "candidate_chunk_index": item["chunk_index"],
            "candidate_score": item.get("positive_score"),
            "candidate_title": item.get("title_guess"),
            "candidate_url": None,
            "answer": positive_answer,
            "verdict": positive_verdict,
            "path_role": "positive",
        }
    )
    if positive_verdict != "CORRECT":
        counts["skip_reasons"]["positive_not_correct"] += 1
        return {
            "kept_row": None,
            "review_rows": review_rows,
            "counts": counts,
        }

    for candidate in get_candidates(item, args.candidate_k):
        candidate_text = candidate.get("text", "")
        answer = None
        try:
            answer = answer_question(
                client_ctx, args.model, query, candidate_text, args.max_retries
            )
            time.sleep(args.sleep_seconds)
            if normalize_answer(answer) == "CANNOT_ANSWER":
                verdict = "CANNOT_ANSWER"
            else:
                verdict = judge_answer(
                    client_ctx,
                    args.model,
                    query,
                    candidate_text,
                    answer,
                    args.max_retries,
                )
                time.sleep(args.sleep_seconds)
        except ApiRequestError as exc:
            counts["skip_reasons"]["api_error"] += 1
            review_rows.append(
                {
                    "example_index": example_index,
                    "query": query,
                    "candidate_rank": candidate.get("rank"),
                    "candidate_article_id": candidate.get("article_id"),
                    "candidate_chunk_index": candidate.get("chunk_index"),
                    "candidate_score": candidate.get("score"),
                    "candidate_title": candidate.get("title"),
                    "candidate_url": candidate.get("url"),
                    "answer": answer,
                    "verdict": "API_ERROR",
                    "path_role": "candidate",
                    "skip_reason": "api_error",
                    "error": str(exc),
                }
            )
            return {
                "kept_row": None,
                "review_rows": review_rows,
                "counts": counts,
            }

        counts["candidate_verdicts"][verdict] += 1
        review_rows.append(
            {
                "example_index": example_index,
                "query": query,
                "candidate_rank": candidate.get("rank"),
                "candidate_article_id": candidate.get("article_id"),
                "candidate_chunk_index": candidate.get("chunk_index"),
                "candidate_score": candidate.get("score"),
                "candidate_title": candidate.get("title"),
                "candidate_url": candidate.get("url"),
                "answer": answer,
                "verdict": verdict,
                "path_role": "candidate",
            }
        )

        if verdict != "CORRECT":
            selected_hns.append(candidate)
            if len(selected_hns) >= args.num_hard_negatives:
                break

    kept_row = None
    if len(selected_hns) >= args.num_hard_negatives:
        kept_row = {
            **item,
            "neg_hits": selected_hns,
            "neg_passages": [cand.get("text", "") for cand in selected_hns],
            "source_positive_rank": item.get("positive_rank"),
            "source_positive_score": item.get("positive_score"),
        }
    else:
        counts["skip_reasons"]["not_enough_hard_negatives"] += 1

    return {
        "kept_row": kept_row,
        "review_rows": review_rows,
        "counts": counts,
    }
