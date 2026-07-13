def encode_screenshot_for_vlm(
    screenshot_path: str, max_pixels: int | None = None
) -> str | None:
    """Encode screenshot for VLM ground truth with configurable max_pixels.

    Unlike encode_screenshot(), this function does NOT apply max_height limit.
    You can control max_pixels to study the effect of resize on VLM performance.

    Args:
        screenshot_path: Path to screenshot file.
        max_pixels: Maximum pixels before resize. If None, uses default (89M).
                    Common values:
                    - 16_777_216 (16M): Qwen3-VL default
                    - 12_845_056 (12.8M): Qwen2-VL default
                    - 4_000_000 (4M): ~4000 tokens
                    - 1_000_000 (1M): ~1000 tokens

    Returns:
        Base64 encoded string, or None if failed.
    """
    if not _init_screenshot_utils():
        return None

    if not screenshot_path or not os.path.exists(screenshot_path):
        return None

    try:
        if _encode_image_for_vlm is None:
            return None
        if max_pixels is not None:
            return _encode_image_for_vlm(screenshot_path, max_pixels=max_pixels)
        return _encode_image_for_vlm(screenshot_path)
    except Exception as e:
        logger.error(f"Image encoding (VLM) failed for {screenshot_path}: {e}")
        return None
