def call_text_llm(client_ctx: dict, model: str, prompt: str, max_retries: int) -> str:
    if client_ctx["provider"] == "openai":
        return call_openai_chat_completions(client_ctx, model, prompt, max_retries)
    return call_gemini_generate_content(client_ctx, model, prompt, max_retries)
