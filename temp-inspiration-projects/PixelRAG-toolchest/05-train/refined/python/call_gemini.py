async def call_gemini(
    client: genai.Client,
    model: str,
    prompt: str,
    token_counter: dict,
) -> str:
    config = GenerateContentConfig(temperature=0.7, max_output_tokens=512)
    t0 = time.time()
    resp = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        ),
    )
    elapsed = time.time() - t0
    usage = resp.usage_metadata
    if usage:
        token_counter["gemini_input"] += getattr(usage, "prompt_token_count", 0)
        token_counter["gemini_output"] += getattr(usage, "candidates_token_count", 0)
        token_counter["gemini_calls"] += 1
        token_counter["gemini_total_time"] += elapsed

    text = ""
    for part in resp.candidates[0].content.parts:
        raw = getattr(part, "text", None)
        if raw and not getattr(part, "thought", False):
            text = raw.strip()
    return text
