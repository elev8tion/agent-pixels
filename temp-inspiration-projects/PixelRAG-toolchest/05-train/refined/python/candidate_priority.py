def candidate_priority(review: dict) -> tuple:
    return (
        int(review["keep"]),
        int(review["naturalness"]) + int(review["simpleqa_style_fit"]),
        int(review["simpleqa_style_fit"]),
        int(review["naturalness"]),
        -int(review["row_id"]),
    )
