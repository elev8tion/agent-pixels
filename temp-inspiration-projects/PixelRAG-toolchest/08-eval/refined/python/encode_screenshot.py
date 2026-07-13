def encode_screenshot(screenshot_path: str) -> str | None:
    """Encode screenshot to base64.

    Args:
        screenshot_path: Path to screenshot file, or already-encoded base64 string.

    Returns:
        Base64 encoded string, or None if failed.
    """
    if not screenshot_path:
        return None

    if not os.path.exists(screenshot_path):
        if len(screenshot_path) > 500 and "/" not in screenshot_path[:20]:
            return screenshot_path
        return None

    if not _init_screenshot_utils():
        return None

    try:
        if _encode_image is None:
            return None
        return _encode_image(screenshot_path)
    except Exception as e:
        logger.error(f"Image encoding failed for {screenshot_path}: {e}")
        return None
