def build_messages_for_livevqa(
    prompt: str,
    image_paths: list[str] | None = None,
    text_chunks: list[str] | None = None,
) -> list[dict]:
    """Build OpenAI-compatible messages for a LiveVQA MCQ call.

    Supports mixed content: images first, then text chunks, then the MCQ prompt.
    """
    content: list[dict] = []
    if image_paths:
        for p in image_paths:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": image_to_base64_url(p)},
                }
            )
    if text_chunks:
        ctx = "\n\n---\n\n".join(text_chunks)
        content.append({"type": "text", "text": ctx})
    content.append({"type": "text", "text": prompt})
    return [{"role": "user", "content": content}]
