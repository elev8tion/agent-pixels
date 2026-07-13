def _call_llm_openai(
    messages: list[dict], model: str, tool_schema: dict, api_key: str, base_url: str
) -> dict:
    """One OpenAI LLM turn with tools. Returns the message dict."""
    body: dict = {
        "model": model,
        "messages": messages,
        "tools": [tool_schema],
        "tool_choice": "auto",
    }
    if _is_local_model(base_url):
        body["max_tokens"] = 4096
    else:
        body["max_completion_tokens"] = 16000
    if _supports_temperature(model):
        body["temperature"] = 0.0
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    last_exc = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=READER_TIMEOUT) as resp:
                d = json.load(resp)
            usage = d.get("usage", {})
            USAGE["prompt_tokens"] += usage.get("prompt_tokens", 0)
            USAGE["completion_tokens"] += usage.get("completion_tokens", 0)
            USAGE["calls"] += 1
            return d["choices"][0]["message"]
        except urllib.error.HTTPError as e:
            last_exc = e
            if e.code in (400, 429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(min(60, 2**attempt + 2))
                continue
            raise
        except urllib.error.URLError as e:
            last_exc = e
            if attempt < 4:
                time.sleep(min(60, 2**attempt + 2))
                continue
            raise
    raise last_exc  # type: ignore[misc]
