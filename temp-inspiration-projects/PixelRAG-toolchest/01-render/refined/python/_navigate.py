async def _navigate(self, tab, article: dict) -> int:
        try:
            await tab.cdp("Page.navigate", {"url": article_url(article)})
        except Exception:
            return TILE_HEIGHT

        try:
            r = await tab.cdp(
                "Runtime.evaluate",
                {
                    "expression": WAIT_FONTS_IMGS,
                    "awaitPromise": True,
                    "returnByValue": True,
                },
            )
            page_h = r["result"]["result"]["value"]
        except Exception:
            page_h = TILE_HEIGHT

        return max(page_h, 1)
