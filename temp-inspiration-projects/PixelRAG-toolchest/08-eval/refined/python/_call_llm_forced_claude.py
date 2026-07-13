def _call_llm_forced_claude(messages: list[dict], model: str, api_key: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    system_str, claude_msgs = _openai_msgs_to_claude(messages)
    last_exc = None
    for attempt in range(4):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=system_str,
                messages=claude_msgs,
            )
            USAGE["prompt_tokens"] += response.usage.input_tokens
            USAGE["completion_tokens"] += response.usage.output_tokens
            USAGE["calls"] += 1
            return "".join(b.text for b in response.content if b.type == "text")
        except anthropic.APIStatusError as e:
            last_exc = e
            if e.status_code in (400, 429, 500, 502, 503, 529) and attempt < 3:
                time.sleep(min(60, 2**attempt + 2))
                continue
            raise
    raise last_exc  # type: ignore[misc]
