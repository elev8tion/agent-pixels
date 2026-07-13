def print_results(results: list[dict]):
    for r in results:
        print(format_result_line(r), flush=True)
        if r["bad_examples"]:
            for ex in r["bad_examples"][:3]:
                print(f"    BAD: {ex}", flush=True)
