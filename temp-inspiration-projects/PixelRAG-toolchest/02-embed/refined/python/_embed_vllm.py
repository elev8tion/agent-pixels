def _embed_vllm(engine, prompt: str, images: list["Image.Image"]) -> list[np.ndarray]:
    """Run embedding on a batch of images via vLLM."""
    inputs = [{"prompt": prompt, "multi_modal_data": {"image": img}} for img in images]
    outputs = engine.embed(inputs)
    # L2 normalize (vLLM pooler does not normalize internally)
    embs = np.array([out.outputs.embedding for out in outputs], dtype=np.float32)
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    embs = embs / np.maximum(norms, 1e-12)
    return [embs[i].astype(np.float16) for i in range(len(embs))]
