def _encode_queries(queries: list[Query], instruction: str | None = None) -> np.ndarray:
    """Encode queries via HF transformers + SDPA (~42ms/query on GPU, exact index alignment).

    Uses the same model + attention backend (SDPA) as the index-building pipeline
    (embed_tiles.py direct_gpu backend), so embeddings are identical (cosine = 1.0).
    """
    import torch

    model = _state["model"]
    processor = _state["processor"]
    device = _state["device"]
    messages_list, images = _parse_queries(queries, instruction)

    texts = [
        processor.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        for msgs in messages_list
    ]
    # Separate image and non-image inputs for the processor
    img_list = [img for img in images if img is not None]
    if img_list:
        inputs = processor(
            text=texts, images=img_list, return_tensors="pt", padding=True
        )
    else:
        inputs = processor(text=texts, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) if hasattr(v, "to") else v for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.model(**inputs)

    # Last-token pooling + L2 normalize — use last_hidden_state (post-RMSNorm)
    last_hidden = outputs.last_hidden_state
    attention_mask = inputs["attention_mask"]
    last_token_indices = attention_mask.sum(dim=1) - 1
    pooled = last_hidden[
        torch.arange(last_hidden.size(0), device=last_hidden.device),
        last_token_indices,
    ]
    pooled = torch.nn.functional.normalize(pooled, p=2, dim=-1)
    return pooled.cpu().float().numpy()
