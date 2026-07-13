def _build_system_prompt(retrieval: str) -> str:
    if retrieval == "pixel":
        tool_name = "search_pixel"
        artifact = "Wikipedia screenshot tiles (PNG images)"
    else:
        tool_name = "search_text"
        artifact = "text passages"
    return SYSTEM_PROMPT_TEMPLATE.format(
        tool_name=tool_name,
        artifact=artifact,
        max_turns=MAX_TURNS,
        default_k=_DEFAULT_TOP_K,
    )
