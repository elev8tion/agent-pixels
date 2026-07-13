def call_vlm(
    client_ctx: dict, model: str, prompt: str, image_path: str, max_retries: int
) -> str:
    if client_ctx["provider"] == "openai":
        return call_openai_chat_completions(
            client_ctx, model, prompt, image_path, max_retries
        )
    return call_gemini_generate_content(
        client_ctx, model, prompt, image_path, max_retries
    )
