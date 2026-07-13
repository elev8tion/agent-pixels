def build_pixel_prompt(question: str, options: list[str], has_photo: bool) -> str:
    opts_str = "\n".join(options)
    if has_photo:
        ctx = "Based on the editorial photo and the article screenshot(s) above"
    else:
        ctx = "Based on the article screenshot(s) above"
    return (
        f"{ctx}, answer the following question.\n\n"
        f"{question}\n\n{opts_str}\n\n"
        "Answer with ONLY the option letter (e.g. A, B, C, D, or E). Do not explain."
    )
