def build_react_messages(
    query: str,
    retrieval_results: list[RetrievalResult],
    assistant_responses: list[str],
    encode_image_fn=None,
    prompt_version: str = "v1",
    is_last_turn: bool = False,
    previous_queries: list[str] | None = None,
) -> list[dict]:
    """Build multi-turn messages for ReAct retrieval loop.

    Args:
        query: Original question text.
        retrieval_results: List of RetrievalResult from each round.
        assistant_responses: List of assistant responses from previous rounds.
        encode_image_fn: Function to encode images to base64.
        prompt_version: "v1" (original) or "v2" (improved).
        is_last_turn: If True, add force-answer instruction.
        previous_queries: List of previous search queries (for v2, to avoid repetition).

    Returns:
        Messages list for the LLM.
    """
    _prompt_map = {
        "v1": SYSTEM_PROMPT_REACT,
        "v2": SYSTEM_PROMPT_REACT_V2,
        "multihop": SYSTEM_PROMPT_REACT_MULTIHOP,
    }
    system_prompt = _prompt_map.get(prompt_version, SYSTEM_PROMPT_REACT_V2)
    messages = [{"role": "system", "content": system_prompt}]

    for turn_idx, retrieval_result in enumerate(retrieval_results):
        # Build user message with evidence images
        if turn_idx == 0:
            user_content: list[dict] = [
                {
                    "type": "text",
                    "text": f"Question: {query}\n\nHere are retrieved Wikipedia evidence tiles:",
                }
            ]
        else:
            text = "Here are new search results for your query:"
            # Remind model of previous queries to avoid repetition (v2 and multihop)
            if prompt_version in ("v2", "multihop") and previous_queries:
                used = previous_queries[:turn_idx]
                if used:
                    text += f"\n⚠️ You already searched: {used}. Do NOT repeat these. Use DIFFERENT keywords."
            user_content = [{"type": "text", "text": text}]

        if retrieval_result.images and encode_image_fn:
            user_content.extend(
                _encode_images_to_content(retrieval_result.images, encode_image_fn)
            )

        if not retrieval_result.has_content:
            user_content.append(
                {"type": "text", "text": "(No results found for this search.)"}
            )

        # On last turn, inject force-answer instruction
        if is_last_turn and turn_idx == len(retrieval_results) - 1:
            user_content.append(
                {
                    "type": "text",
                    "text": (
                        "\n⚠️ This is your FINAL turn. You MUST provide an answer now — do NOT search again. "
                        "Give your best answer based on ALL evidence seen so far. If uncertain, make your best guess."
                    ),
                }
            )

        messages.append({"role": "user", "content": user_content})

        # Add assistant response if we have one for this turn
        if turn_idx < len(assistant_responses):
            messages.append(
                {"role": "assistant", "content": assistant_responses[turn_idx]}
            )

    return messages
