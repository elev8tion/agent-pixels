async def get_hits(self, query: str, example: dict) -> list[dict]:
        """Return raw per-hit dicts (title/text/url/score/...) for this example.

        Used by wrappers that need per-chunk granularity (e.g. RenderedTextWrapper).
        Uses the same cache as retrieve().
        """
        await self.retrieve(query, example)
        return self._cache.get(example.get("id", "unknown"), [])
