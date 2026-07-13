def _parse_queries(
    queries: list[Query], instruction: str | None = None
) -> tuple[list[dict], list[Image.Image | None]]:
    """Parse queries into chat messages and optional images."""
    instr = DEFAULT_INSTRUCTION if instruction is None else instruction
    messages_list = []
    images = []
    for q in queries:
        # Build chat messages for apply_chat_template
        sys_content = [{"type": "text", "text": instr}]
        user_content = []
        img = None
        if q.image:
            # Accept both a raw base64 string and a data URL
            # ("data:image/png;base64,...") — strip the prefix if present,
            # otherwise b64decode chokes on it ("Incorrect padding").
            img_data = q.image
            if img_data.startswith("data:"):
                img_data = img_data.split(",", 1)[-1]
            img_bytes = base64.b64decode(img_data)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            user_content.append({"type": "image", "image": img})
        if q.text:
            user_content.append({"type": "text", "text": q.text})
        if not user_content:
            raise HTTPException(
                status_code=400, detail="Query must have text, image, or both"
            )
        messages_list.append(
            [
                {"role": "system", "content": sys_content},
                {"role": "user", "content": user_content},
            ]
        )
        images.append(img)
    return messages_list, images
