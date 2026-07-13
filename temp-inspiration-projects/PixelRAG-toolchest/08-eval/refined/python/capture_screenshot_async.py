async def capture_screenshot_async(
    example: dict, screenshot_dir: str = "screenshots"
) -> str | None:
    """Async wrapper for screenshot capture."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, capture_screenshot_for_example, example, screenshot_dir
    )
