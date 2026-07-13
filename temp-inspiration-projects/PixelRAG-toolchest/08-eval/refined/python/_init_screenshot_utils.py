def _init_screenshot_utils():
    """Initialize screenshot utilities (lazy import)."""
    global _capture_screenshot, _encode_image, _encode_image_for_vlm
    if _capture_screenshot is not None:
        return True

    try:
        from .screenshot import capture_screenshot, encode_image, encode_image_for_vlm

        _capture_screenshot = capture_screenshot
        _encode_image = encode_image
        _encode_image_for_vlm = encode_image_for_vlm
        return True
    except ImportError:
        logger.warning("Screenshot utilities not available")
        return False
