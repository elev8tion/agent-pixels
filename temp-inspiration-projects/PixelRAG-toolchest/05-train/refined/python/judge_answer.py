def judge_answer(
    client_ctx: dict,
    model: str,
    question: str,
    passage: str,
    answer: str,
    max_retries: int,
) -> str:
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        question=question, candidate_answer=answer, passage=passage
    )
    verdict = call_text_llm(client_ctx, model, prompt, max_retries)
    verdict = verdict.strip().upper().replace('"', "").replace("`", "")
    compact_verdict = verdict.replace("-", "_").replace(" ", "_")
    for candidate in ("CANNOT_ANSWER", "CORRECT", "WRONG"):
        if candidate in compact_verdict:
            return candidate
    if any(
        marker in verdict
        for marker in (
            "NOT ENOUGH INFORMATION",
            "CANNOT BE VERIFIED",
            "CANNOT VERIFY",
            "CANNOT DETERMINE",
            "UNABLE TO DETERMINE",
            "NOT STATED",
            "NOT PROVIDED",
            "NOT MENTIONED",
            "DOES NOT SAY",
            "DOESN'T SAY",
        )
    ):
        return "CANNOT_ANSWER"
    return "WRONG"
