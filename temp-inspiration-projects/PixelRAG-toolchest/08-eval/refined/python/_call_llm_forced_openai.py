def _call_llm_forced_openai(
    messages: list[dict], model: str, api_key: str, base_url: str
) -> str:
    """Final forced-answer call without tools."""
    body: dict = {"model": model, "messages": messages}
    if _is_local_model(base_url):
        body["max_tokens"] = 4096
    else:
        body["max_completion_tokens"] = 4096
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
    with urllib.request.urlopen(req, timeout=READER_TIMEOUT) as resp:
        d = json.load(resp)
    USAGE["prompt_tokens"] += d.get("usage", {}).get("prompt_tokens", 0)
    USAGE["completion_tokens"] += d.get("usage", {}).get("completion_tokens", 0)
    USAGE["calls"] += 1
    return d["choices"][0]["message"].get("content", "")
