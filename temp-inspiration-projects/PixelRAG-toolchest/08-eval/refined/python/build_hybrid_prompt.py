def build_hybrid_prompt(
    question: str,
    options: list[str],
    n_tiles: int,
    n_chunks: int,
    has_photo: bool,
) -> str:
    opts_str = "\n".join(options)
    parts = []
    if has_photo:
        parts.append("the editorial photo")
    if n_tiles > 0:
        parts.append(f"the {n_tiles} article screenshot(s)")
    if n_chunks > 0:
        parts.append(f"the {n_chunks} article excerpt(s)")
    intro = "Use " + " and ".join(parts) + " above to answer the following question."
    return (
        f"{intro}\n\n"
        f"{question}\n\n{opts_str}\n\n"
        "Answer with ONLY the option letter (e.g. A, B, C, D, or E). Do not explain."
    )
