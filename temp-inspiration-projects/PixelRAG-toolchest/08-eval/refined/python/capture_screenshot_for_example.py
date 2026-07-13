def capture_screenshot_for_example(
    example: dict, screenshot_dir: str = "screenshots"
) -> str | None:
    """Capture screenshot for a single example.

    Args:
        example: Example dict with metadata containing URL.
        screenshot_dir: Directory to save screenshots.

    Returns:
        Path to screenshot file, or None if failed.
    """
    if not _init_screenshot_utils():
        return None

    target_url = extract_url_from_metadata(example)
    if not target_url:
        return None

    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_filename = f"{example['id']}_fullhd.png"
    screenshot_path = os.path.join(screenshot_dir, screenshot_filename)

    # Check if valid screenshot already exists
    if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
        logger.debug(f"Screenshot exists: {screenshot_path}")
        return screenshot_path

    # Capture screenshot
    try:
        if _capture_screenshot is None:
            return None
        success = _capture_screenshot(target_url, screenshot_path, True)
        if (
            success
            and os.path.exists(screenshot_path)
            and os.path.getsize(screenshot_path) > 0
        ):
            file_size = os.path.getsize(screenshot_path) // 1024
            logger.info(f"Screenshot saved: {screenshot_path} ({file_size}KB)")
            return screenshot_path
        else:
            logger.warning(
                f"Screenshot failed (no output): {target_url} -> {screenshot_path}"
            )
    except Exception as e:
        logger.error(f"Screenshot error for {target_url}: {e}")

    return None
