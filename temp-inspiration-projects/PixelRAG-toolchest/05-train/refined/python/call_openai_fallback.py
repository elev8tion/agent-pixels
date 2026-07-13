async def call_openai_fallback(
    client: openai.AsyncOpenAI,
    model: str,
    prompt: str,
    token_counter: dict,
) -> str:
    t0 = time.time()
    resp = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512,
    )
    elapsed = time.time() - t0
    token_counter["openai_input"] += resp.usage.prompt_tokens
    token_counter["openai_output"] += resp.usage.completion_tokens
    token_counter["openai_calls"] += 1
    token_counter["openai_total_time"] += elapsed
    return (resp.choices[0].message.content or "").strip()
