def call_gemini_generate_content(
    client_ctx: dict, model: str, prompt: str, max_retries: int
) -> str:
    from google.genai.types import GenerateContentConfig

    config = GenerateContentConfig(temperature=0, max_output_tokens=128)
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
            text = getattr(resp, "text", None)
            if text:
                return text.strip()
            candidates = getattr(resp, "candidates", None) or []
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                parts = getattr(content, "parts", None) or []
                for part in parts:
                    raw = getattr(part, "text", None)
                    if raw and not getattr(part, "thought", False):
                        return raw.strip()
            raise ApiRequestError("Gemini returned no text content")
        except Exception as exc:
            if attempt == max_retries:
                raise ApiRequestError(f"{type(exc).__name__}: {exc}") from exc
            wait_seconds = min(2**attempt, 20)
            err = str(exc)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                wait_seconds = max(wait_seconds, 15)
            time.sleep(wait_seconds)
    raise RuntimeError("Unreachable")
