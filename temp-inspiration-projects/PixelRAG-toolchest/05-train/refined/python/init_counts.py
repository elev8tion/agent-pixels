def init_counts() -> dict:
    return {
        "candidate_verdicts": {"CORRECT": 0, "WRONG": 0, "CANNOT_ANSWER": 0},
        "skip_reasons": {
            "not_enough_hard_negatives": 0,
            "positive_not_correct": 0,
            "api_error": 0,
        },
    }
