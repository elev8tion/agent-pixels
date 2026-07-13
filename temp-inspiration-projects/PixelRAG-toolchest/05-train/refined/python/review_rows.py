def review_rows(
    rows: list[dict],
    args: argparse.Namespace,
    client_ctx: dict,
    references: list[dict],
    reviews_path: Path,
) -> dict[int, dict]:
    existing = load_existing_reviews(reviews_path) if args.resume else {}
    pending = [row for row in rows if row["row_id"] not in existing]
    total = len(rows)

    if pending:
        reviews_path.parent.mkdir(parents=True, exist_ok=True)
        with reviews_path.open("a") as reviews_file:
            with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                futures = {}
                pending_batches = [
                    pending[start : start + args.batch_size]
                    for start in range(0, len(pending), args.batch_size)
                ]
                next_batch_idx = 0

                while (
                    next_batch_idx < len(pending_batches)
                    and len(futures) < args.concurrency
                ):
                    batch = pending_batches[next_batch_idx]
                    future = executor.submit(
                        score_batch, client_ctx, args, references, batch
                    )
                    futures[future] = batch
                    next_batch_idx += 1

                completed = 0
                while futures:
                    done, _ = wait(futures.keys(), return_when=FIRST_COMPLETED)
                    for future in done:
                        batch = futures.pop(future)
                        decisions = future.result()
                        for row, decision in zip(batch, decisions):
                            review = {
                                "row_id": row["row_id"],
                                "query": row["query"],
                                "source_file": row["source_file"],
                                "source_line": row["source_line"],
                                **decision,
                            }
                            existing[row["row_id"]] = review
                            reviews_file.write(
                                json.dumps(review, ensure_ascii=False) + "\n"
                            )
                        reviews_file.flush()
                        completed += len(batch)
                        print(
                            f"Reviewed {len(existing)}/{total} rows "
                            f"(new {completed}/{len(pending)})",
                            flush=True,
                        )
                        if next_batch_idx < len(pending_batches):
                            next_batch = pending_batches[next_batch_idx]
                            next_future = executor.submit(
                                score_batch, client_ctx, args, references, next_batch
                            )
                            futures[next_future] = next_batch
                            next_batch_idx += 1
    return existing
