def call_openai_chat_completions(
    client_ctx: dict, model: str, prompt: str, max_retries: int
) -> str:
    headers = {
        "Authorization": f"Bearer {client_ctx['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(
                CHAT_COMPLETIONS_URL, headers=headers, json=payload, timeout=180
            )
            resp.raise_for_status()
            data = resp.json()
            usage = data.get("usage", {})
            update_usage(
                client_ctx,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
            )
            return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            if attempt == max_retries:
                raise ApiRequestError(f"{type(exc).__name__}: {exc}") from exc
            time.sleep(min(2**attempt, 20))
    raise RuntimeError("Unreachable")
