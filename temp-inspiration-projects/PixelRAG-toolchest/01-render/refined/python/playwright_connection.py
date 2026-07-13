class PlaywrightConnection:
    """Playwright-managed CDP connection."""

    def __init__(self, page, cdp_session, browser, pw):
        self._page = page
        self._cdp = cdp_session
        self._browser = browser
        self._pw = pw

    async def cdp(self, method: str, params: dict | None = None) -> dict:
        result = await self._cdp.send(method, params or {})
        return {"result": result}

    async def close(self):
        try:
            await self._browser.close()
        except Exception:
            pass
        try:
            await self._pw.stop()
        except Exception:
            pass
