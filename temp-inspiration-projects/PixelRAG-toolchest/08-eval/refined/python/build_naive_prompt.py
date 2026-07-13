def build_naive_prompt(question: str, options: list[str], has_photo: bool) -> str:
    opts_str = "\n".join(options)
    if has_photo:
        return (
            "Based on the editorial photo above, answer the following question.\n\n"
            f"{question}\n\n{opts_str}\n\n"
            "Answer with ONLY the option letter (e.g. A, B, C, D, or E). Do not explain."
        )
    return (
        f"{question}\n\n{opts_str}\n\n"
        "Answer with ONLY the option letter (e.g. A, B, C, D, or E). Do not explain."
    )
