class ChromeConnection(Protocol):
    """Abstract connection to one Chrome process."""

    async def cdp(self, method: str, params: dict | None = None) -> dict:
        """Send a CDP command, wait for response."""
        ...

    async def close(self) -> None: ...
