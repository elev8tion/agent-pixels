def print_statistics(results: list[dict], args) -> None:
    """Print evaluation statistics."""
    total = len(results)
    if total == 0:
        print("No results to report.")
        return

    # Count success/failure
    success_count = sum(1 for r in results if r.get("success", False))
    failure_count = total - success_count

    print("-" * 40)
    print(f"Total: {total} examples")
    print(f"  Success: {success_count} ({success_count / total * 100:.1f}%)")
    print(f"  Failed: {failure_count} ({failure_count / total * 100:.1f}%)")

    # Timing statistics
    successful_results = [
        r for r in results if r.get("success", False) and r.get("timing")
    ]
    if successful_results:
        retrieval_times = [
            r["timing"]["retrieval_time"]
            for r in successful_results
            if r["timing"].get("retrieval_time") is not None
        ]
        llm_times = [
            r["timing"]["llm_time"]
            for r in successful_results
            if r["timing"].get("llm_time") is not None
        ]
        total_times = [
            r["timing"]["total_time"]
            for r in successful_results
            if r["timing"].get("total_time") is not None
        ]

        if retrieval_times:
            print(
                f"\nTiming Statistics (for {len(successful_results)} successful requests):"
            )
            print("  Jina read time:")
            print(f"    Mean: {sum(retrieval_times) / len(retrieval_times):.2f}s")
            print(f"    Min: {min(retrieval_times):.2f}s")
            print(f"    Max: {max(retrieval_times):.2f}s")
            print(
                f"    Median: {sorted(retrieval_times)[len(retrieval_times) // 2]:.2f}s"
            )

        if llm_times:
            print("  LLM call time:")
            print(f"    Mean: {sum(llm_times) / len(llm_times):.2f}s")
            print(f"    Min: {min(llm_times):.2f}s")
            print(f"    Max: {max(llm_times):.2f}s")
            print(f"    Median: {sorted(llm_times)[len(llm_times) // 2]:.2f}s")

        if total_times:
            print("  Total time:")
            print(f"    Mean: {sum(total_times) / len(total_times):.2f}s")
            print(f"    Min: {min(total_times):.2f}s")
            print(f"    Max: {max(total_times):.2f}s")
            print(f"    Median: {sorted(total_times)[len(total_times) // 2]:.2f}s")

    # Count by retrieval type (only for successful)
    successful = [r for r in results if r.get("success", False)]
    if successful:
        type_counts = {}
        for r in successful:
            rt = r.get("retrieval_type", "unknown")
            type_counts[rt] = type_counts.get(rt, 0) + 1

        print("\nRetrieval types (successful only):")
        for rt, count in type_counts.items():
            print(f"  {rt}: {count} ({count / len(successful) * 100:.1f}%)")

    # Retrieval accuracy (for vector mode)
    # Checks if any of the top-k retrieved tiles come from the correct Wikipedia page
    if args.retrieval_augment or args.use_tiled_retrieval or args.local_api:
        retrieval_results = [r for r in results if r.get("retrieved_images")]
        if retrieval_results:
            correct = 0
            for r in retrieval_results:
                # Try to get ground truth URL from metadata
                gt_url = extract_url_from_metadata(r.get("original_data", {}))

                if not gt_url:
                    # Fallback: match by example_id in tile filename
                    example_id = r.get("example_id", "")
                    for img_info in r.get("retrieved_images", []):
                        img_path = img_info.get("original_path") or img_info.get(
                            "path", ""
                        )
                        img_basename = os.path.basename(img_path)
                        if example_id in img_basename:
                            correct += 1
                            break
                else:
                    # Check if any retrieved tile's URL matches the ground truth URL
                    # retrieved_url is a string of comma-separated URLs from tiles
                    retrieved_url = r.get("used_url", "")
                    # Check if the ground truth URL is contained in the retrieved URLs
                    if gt_url in retrieved_url:
                        correct += 1

            print("\nRetrieval Accuracy:")
            print(
                f"  Correct (top-{args.retrieval_top_k}): {correct}/{len(retrieval_results)} ({correct / len(retrieval_results) * 100:.1f}%)"
            )

    # ReAct turn statistics
    react_results = [r for r in results if r.get("react_turns") is not None]
    if react_results:
        turns = [r["react_turns"] for r in react_results]
        from collections import Counter

        turn_counts = Counter(turns)
        print("\nReAct Turn Distribution:")
        for t in sorted(turn_counts):
            print(
                f"  {t} turn(s): {turn_counts[t]} ({turn_counts[t] / len(react_results) * 100:.1f}%)"
            )
        print(f"  Average turns: {sum(turns) / len(turns):.2f}")
        multi_turn = sum(1 for t in turns if t > 1)
        print(
            f"  Examples needing re-search: {multi_turn}/{len(react_results)} ({multi_turn / len(react_results) * 100:.1f}%)"
        )

    print("-" * 40)
    print(f"Results saved to {args.output}")
