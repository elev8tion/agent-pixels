def react_loop(
    question: str,
    model: str,
    retrieval: str,
    api_key: str,
    base_url: str,
    max_turns: int | None = None,
) -> dict:
    """Run the ReAct loop. Returns dict with 'final', 'turns', 'searches', 'trace', 'k_values'."""
    if max_turns is None:
        max_turns = MAX_TURNS
    system_prompt = _build_system_prompt(retrieval)
    tool_schema = copy.deepcopy(
        SEARCH_PIXEL_TOOL if retrieval == "pixel" else SEARCH_TEXT_TOOL
    )
    tool_name = "search_pixel" if retrieval == "pixel" else "search_text"
    use_claude = _is_claude_model(model)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    trace = []
    n_searches = 0
    k_values: list[int] = []

    for turn in range(max_turns):
        if use_claude:
            msg = _call_llm_claude(messages, model, tool_schema, api_key)
        else:
            msg = _call_llm_openai(messages, model, tool_schema, api_key, base_url)

        assistant_entry = {"role": "assistant", "content": msg.get("content")}
        if msg.get("tool_calls"):
            assistant_entry["tool_calls"] = msg["tool_calls"]
        messages.append(assistant_entry)

        if msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                fn = tc.get("function", {})
                name = fn.get("name", "")
                try:
                    args = json.loads(fn.get("arguments", "{}"))
                except Exception:
                    args = {}

                if name == tool_name:
                    n_searches += 1
                    USAGE["tool_calls"] += 1
                    q = args.get("query", "")
                    k = max(1, min(args.get("top_k") or _DEFAULT_TOP_K, _MAX_TOP_K))
                    k_values.append(k)
                    trace.append((turn, "search", f"k={k} {q[:80]}"))

                    if retrieval == "text":
                        result = _search_text(q, n_docs=k)
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tc["id"],
                                "content": result[:RESULT_TRUNCATE_CHARS],
                            }
                        )
                    else:
                        image_parts = _search_pixel(q, n_docs=k)
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tc["id"],
                                "content": image_parts,
                            }
                        )
                else:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": f"[unknown tool: {name}]",
                        }
                    )
        else:
            # No tool calls -> final answer
            content = msg.get("content", "") or ""
            trace.append((turn, "answer", content[:80]))
            return {
                "final": content,
                "turns": turn + 1,
                "searches": n_searches,
                "trace": trace,
                "k_values": k_values,
            }

    # Hit max_turns: force a final answer
    messages.append(
        {
            "role": "user",
            "content": "You must now provide the final answer. Output exactly one line:\nAnswers: {your answer}",
        }
    )
    if use_claude:
        forced = _call_llm_forced_claude(messages, model, api_key)
    else:
        forced = _call_llm_forced_openai(messages, model, api_key, base_url)
    trace.append((max_turns, "forced_answer", forced[:80]))
    return {
        "final": forced,
        "turns": max_turns + 1,
        "searches": n_searches,
        "trace": trace,
        "k_values": k_values,
    }
