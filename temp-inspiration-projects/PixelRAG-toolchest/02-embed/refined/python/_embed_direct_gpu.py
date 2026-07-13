def _embed_direct_gpu(
    engine, prompt: str, images: list["Image.Image"]
) -> list[np.ndarray]:
    """Embed images using direct model forward with GPU preprocessing.

    The prompt arg is the chat template text (same format as sglang).
    We pass device='cuda' to the processor so all image tensor ops
    (resize, normalize, stack, cat) run on GPU instead of CPU.
    """
    import torch

    model, processor = engine

    # Build per-image message format for the processor
    messages_batch = [
        [
            {"role": "system", "content": [{"type": "text", "text": _INSTRUCTION}]},
            {"role": "user", "content": [{"type": "image", "image": img}]},
        ]
        for img in images
    ]
    texts = [
        processor.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
        for m in messages_batch
    ]
    # GPU-accelerated preprocessing: device="cuda" moves resize/normalize/stack to GPU
    inputs = processor(
        text=texts, images=images, return_tensors="pt", padding=True, device="cuda"
    )
    inputs = {k: v.to("cuda") if hasattr(v, "to") else v for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.model(**inputs)

    # Last-token pooling — use last_hidden_state (post-RMSNorm)
    last_hidden = outputs.last_hidden_state  # (batch, seq_len, hidden_dim)
    attention_mask = inputs["attention_mask"]  # (batch, seq_len)
    # Find the last non-padding token for each sequence
    last_token_indices = attention_mask.sum(dim=1) - 1  # (batch,)
    pooled = last_hidden[
        torch.arange(last_hidden.size(0), device=last_hidden.device), last_token_indices
    ]
    # L2 normalize
    pooled = torch.nn.functional.normalize(pooled, p=2, dim=-1)

    return [emb.cpu().float().numpy().astype(np.float16) for emb in pooled]
