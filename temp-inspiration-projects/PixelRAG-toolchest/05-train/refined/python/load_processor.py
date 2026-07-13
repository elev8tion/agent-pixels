def load_processor(
    model_path: str, min_pixels: int = 128 * 28 * 28, max_pixels: int = 256 * 28 * 28
):
    """Load the processor with configurable image resolution.

    Default resolution is reduced from the model default (~1.3M pixels) to
    ~100K-200K pixels for training speed. Full resolution can be restored
    for inference by setting max_pixels=1280*28*28.
    """
    return AutoProcessor.from_pretrained(
        model_path,
        trust_remote_code=True,
        min_pixels=min_pixels,
        max_pixels=max_pixels,
    )
