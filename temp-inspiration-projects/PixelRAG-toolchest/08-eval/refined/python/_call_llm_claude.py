def _call_llm_claude(
    messages: list[dict], model: str, tool_schema: dict, api_key: str
) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    system_str, claude_msgs = _openai_msgs_to_claude(messages)
    claude_tool = _openai_tool_to_claude(tool_schema)
    last_exc = None
    for attempt in range(5):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=16000,
                system=system_str,
                messages=claude_msgs,
                tools=[claude_tool],
                tool_choice={"type": "auto"},
            )
            USAGE["prompt_tokens"] += response.usage.input_tokens
            USAGE["completion_tokens"] += response.usage.output_tokens
            USAGE["calls"] += 1
            return _claude_response_to_openai(response)
        except anthropic.APIStatusError as e:
            last_exc = e
            if e.status_code in (400, 429, 500, 502, 503, 529) and attempt < 4:
                time.sleep(min(60, 2**attempt + 2))
                continue
            raise
        except Exception as e:
            last_exc = e
            if attempt < 4:
                time.sleep(min(60, 2**attempt + 2))
                continue
            raise
    raise last_exc  # type: ignore[misc]
