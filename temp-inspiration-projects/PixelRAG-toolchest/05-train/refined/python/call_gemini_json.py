def call_gemini_json(client_ctx: dict, model: str, prompt: str, max_retries: int):
    from google.genai.types import GenerateContentConfig

    config = GenerateContentConfig(
        temperature=0,
        max_output_tokens=8192,
        response_mime_type="application/json",
    )
    for attempt in range(1, max_retries + 1):
        try:
            resp = client_ctx["client"].models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            usage = getattr(resp, "usage_metadata", None)
            if usage is not None:
                update_usage(
                    client_ctx,
                    prompt_tokens=getattr(usage, "prompt_token_count", 0),
                    completion_tokens=getattr(usage, "candidates_token_count", 0),
                )
            text = getattr(resp, "text", "") or ""
            return parse_json_from_text(text)
        except Exception:
            if attempt == max_retries:
                raise
            time.sleep(min(2**attempt, 20))
    raise RuntimeError("unreachable")
