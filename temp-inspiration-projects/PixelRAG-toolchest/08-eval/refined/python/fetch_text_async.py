async def fetch_text_async(
    example: dict, max_chars: int = 50000, text_cache: dict | None = None
) -> tuple[str | None, str | None]:
    """Async wrapper for text fetching."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, fetch_text_for_example, example, max_chars, text_cache
    )
