async def encode_screenshot_async(screenshot_path: str) -> str | None:
    """Async wrapper for screenshot encoding."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, encode_screenshot, screenshot_path)
