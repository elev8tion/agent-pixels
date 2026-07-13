def embed_items(
    items: list[dict],
    model_name: str,
    device: str = "cpu",
    instruction: str = "",
) -> np.ndarray:
    """Embed image items using transformers on the given device."""
    import torch
    from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

    device = _resolve_device(device)
    dtype = torch.float32 if device == "cpu" else torch.float16

    logger.info("Loading model %s on %s (%s)...", model_name, device, dtype)
    processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=dtype,
        attn_implementation="sdpa",
    ).eval()
    if device != "cpu":
        model = model.to(device)
    logger.info("Model loaded on %s", device)

    dim = model.config.text_config.hidden_size
    embeddings = np.zeros((len(items), dim), dtype=np.float16)

    prefix = f"Instruct: {instruction}\n" if instruction else ""

    for i, item in enumerate(tqdm(items, desc="Embedding")):
        img = Image.open(item["path"]).convert("RGB")
        img = _clamp_width(img)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img},
                    {"type": "text", "text": prefix + "What is shown in this image?"},
                ],
            }
        ]

        text = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = processor(text=[text], images=[img], return_tensors="pt", padding=True)
        if device != "cpu":
            inputs = {
                k: v.to(device) if hasattr(v, "to") else v for k, v in inputs.items()
            }

        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)
            last_hidden = outputs.hidden_states[-1]
            seq_lens = inputs["attention_mask"].sum(dim=1)
            last_idx = seq_lens - 1
            pooled = last_hidden[0, last_idx[0]]
            pooled = pooled / pooled.norm()
            embeddings[i] = pooled.cpu().numpy().astype(np.float16)

        if (i + 1) % 10 == 0:
            logger.info("Embedded %d/%d", i + 1, len(items))

    return embeddings
