def merge_counts(summary: dict, counts: dict) -> None:
    for verdict, count in counts["candidate_verdicts"].items():
        summary["candidate_verdicts"][verdict] += count
    for key, count in counts["skip_reasons"].items():
        summary["skip_reasons"][key] += count
