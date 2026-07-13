def process_one(client, model, ex, image_root):
    img_path = os.path.join(image_root, ex["chunk_path"])
    img_url = encode_image(img_path) if os.path.exists(img_path) else None
    if img_url is None:
        return {**ex, "reasoning": None, "_error": "no_image"}
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": PROMPT.format(
                                query=ex["query"], answer=ex["answer"]
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": img_url, "detail": "high"},
                        },
                    ],
                }
            ],
            max_tokens=200,
            temperature=0.3,
        )
        reasoning = resp.choices[0].message.content.strip()
        return {**ex, "reasoning": reasoning}
    except Exception as e:
        return {**ex, "reasoning": None, "_error": str(e)[:200]}
