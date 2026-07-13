def _openai_msgs_to_claude(messages: list[dict]) -> tuple[str, list[dict]]:
    """Convert OpenAI messages to (system_str, claude_messages)."""
    system_parts = []
    claude_msgs: list[dict] = []
    for m in messages:
        role = m.get("role", "")
        if role == "system":
            system_parts.append(
                m["content"] if isinstance(m["content"], str) else str(m["content"])
            )
        elif role == "user":
            content = m["content"]
            if isinstance(content, str):
                claude_msgs.append({"role": "user", "content": content})
            elif isinstance(content, list):
                blocks = []
                for part in content:
                    if part.get("type") == "text":
                        blocks.append({"type": "text", "text": part["text"]})
                    elif part.get("type") == "image_url":
                        url = part["image_url"]["url"]
                        if url.startswith("data:"):
                            header, b64data = url.split(",", 1)
                            media_type = header.split(":")[1].split(";")[0]
                            blocks.append(
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": b64data,
                                    },
                                }
                            )
                claude_msgs.append({"role": "user", "content": blocks})
        elif role == "assistant":
            blocks = []
            text = m.get("content")
            if text:
                blocks.append({"type": "text", "text": text})
            for tc in m.get("tool_calls", []):
                fn = tc.get("function", {})
                try:
                    inp = json.loads(fn.get("arguments", "{}"))
                except Exception:
                    inp = {}
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": fn["name"],
                        "input": inp,
                    }
                )
            claude_msgs.append(
                {
                    "role": "assistant",
                    "content": blocks or [{"type": "text", "text": ""}],
                }
            )
        elif role == "tool":
            tool_content = m.get("content", "")
            result_blocks = []
            if isinstance(tool_content, str):
                result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": m.get("tool_call_id", ""),
                        "content": tool_content,
                    }
                )
            elif isinstance(tool_content, list):
                inner = []
                for part in tool_content:
                    if part.get("type") == "text":
                        inner.append({"type": "text", "text": part["text"]})
                    elif part.get("type") == "image_url":
                        url = part["image_url"]["url"]
                        if url.startswith("data:"):
                            header, b64data = url.split(",", 1)
                            media_type = header.split(":")[1].split(";")[0]
                            inner.append(
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": b64data,
                                    },
                                }
                            )
                result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": m.get("tool_call_id", ""),
                        "content": inner,
                    }
                )
            if (
                claude_msgs
                and claude_msgs[-1]["role"] == "user"
                and isinstance(claude_msgs[-1]["content"], list)
                and claude_msgs[-1]["content"]
                and claude_msgs[-1]["content"][0].get("type") == "tool_result"
            ):
                claude_msgs[-1]["content"].extend(result_blocks)
            else:
                claude_msgs.append({"role": "user", "content": result_blocks})
    return "\n\n".join(system_parts), claude_msgs
