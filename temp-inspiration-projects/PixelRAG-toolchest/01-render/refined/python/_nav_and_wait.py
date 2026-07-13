async def _nav_and_wait(self, conn, article: dict) -> int:
        """Phase 1: Navigate + wait for all resources. Returns page_height."""
        await conn.cdp("Page.navigate", {"url": article_url(article)})
        try:
            r = await conn.cdp(
                "Runtime.evaluate",
                {"expression": WAIT_ALL, "awaitPromise": True, "returnByValue": True},
            )
            return r["result"]["result"]["value"] or TILE_HEIGHT
        except Exception:
            return TILE_HEIGHT
