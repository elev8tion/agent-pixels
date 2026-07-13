def run_agent(
    question: str,
    endpoint: str,
    model: str = "claude-sonnet-4-20250514",
    verbose: bool = False,
) -> str:
    """Run the agent loop: send question → handle tool calls → return final answer."""
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": question}]

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if verbose:
            print(
                f"  [stop_reason={response.stop_reason}, usage={response.usage}]",
                file=sys.stderr,
            )

        if response.stop_reason == "end_turn":
            # Extract text from response
            text_parts = [b.text for b in response.content if b.type == "text"]
            return "\n".join(text_parts)

        # Handle tool use
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                if verbose:
                    print(
                        f"  [tool: {block.name}({json.dumps(block.input, ensure_ascii=False)})]",
                        file=sys.stderr,
                    )
                result = handle_tool_call(block.name, block.input, endpoint)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

        if not tool_results:
            # No tool calls and not end_turn — shouldn't happen, but handle gracefully
            text_parts = [b.text for b in response.content if b.type == "text"]
            return "\n".join(text_parts) if text_parts else "(no response)"

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
