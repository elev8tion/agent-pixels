def build_text_prompt(
    question: str, options: list[str], passages: list[str], has_photo: bool
) -> str:
    ctx = "\n\n---\n\n".join(passages) if passages else "(no context retrieved)"
    opts_str = "\n".join(options)
    if has_photo:
        intro = "Use the editorial photo above and the following article excerpts to answer the question."
    else:
        intro = "Use the following article excerpts to answer the question."
    return (
        f"{intro}\n\n"
        f"{ctx}\n\n"
        f"---\n\n"
        f"Question: {question}\n\n"
        f"{opts_str}\n\n"
        "Answer with ONLY the option letter (A, B, C, D, or E). Do not explain."
    )
