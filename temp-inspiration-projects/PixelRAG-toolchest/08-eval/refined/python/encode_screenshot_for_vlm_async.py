async def encode_screenshot_for_vlm_async(
    screenshot_path: str, max_pixels: int | None = None
) -> str | None:
    """Async wrapper for VLM screenshot encoding."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, encode_screenshot_for_vlm, screenshot_path, max_pixels
    )
