def _build_fewshot_turns(demos: list[dict], encode_image_fn) -> list[dict]:
    """Build a list of (user, assistant) message turns for in-context few-shot.

    Each demo becomes: user={Q text + demo image} → assistant={answer}. The
    chat-tuned model treats these as prior conversation turns rather than
    mixing them with the current question's evidence — this is the canonical
    few-shot format for instruction-tuned chat models.
    """
    turns: list[dict] = []
    for demo in demos:
        user_content: list[dict] = [
            {"type": "text", "text": f"Question: {demo['question']}"},
        ]
        img_path = demo.get("image_path")
        if img_path and encode_image_fn and os.path.exists(img_path):
            try:
                b64 = encode_image_fn(img_path)
                if b64:
                    user_content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"},
                        }
                    )
            except Exception as e:
                logger.warning(f"Failed to encode few-shot image {img_path}: {e}")
        turns.append({"role": "user", "content": user_content})
        turns.append({"role": "assistant", "content": demo["answer"]})
    return turns
