def answer_question(
    client_ctx: dict, model: str, question: str, passage: str, max_retries: int
) -> str:
    prompt = ANSWER_PROMPT_TEMPLATE.format(question=question, passage=passage)
    return call_text_llm(client_ctx, model, prompt, max_retries)
