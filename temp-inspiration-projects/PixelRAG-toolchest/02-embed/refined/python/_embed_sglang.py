def _embed_sglang(engine, prompt: str, images: list["Image.Image"]) -> list[np.ndarray]:
    """Run embedding on a batch via SGLang engine.encode().

    SGLang encode() takes prompts + image_data separately.
    Image data is passed as PIL Images (supported since sglang 0.5.x).
    """
    prompts = [prompt] * len(images)
    outputs = engine.encode(prompts, image_data=images)
    # L2 normalize (sglang encode() does not normalize internally)
    embs = np.array([out["embedding"] for out in outputs], dtype=np.float32)
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    embs = embs / np.maximum(norms, 1e-12)
    return [embs[i].astype(np.float16) for i in range(len(embs))]
