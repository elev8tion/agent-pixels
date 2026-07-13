def update_usage(
    client_ctx: dict, prompt_tokens: int = 0, completion_tokens: int = 0
) -> None:
    with client_ctx["usage_lock"]:
        client_ctx["usage"]["prompt_tokens"] += int(prompt_tokens or 0)
        client_ctx["usage"]["completion_tokens"] += int(completion_tokens or 0)
        client_ctx["usage"]["calls"] += 1
