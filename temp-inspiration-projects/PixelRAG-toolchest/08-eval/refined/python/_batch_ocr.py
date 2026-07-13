async def _batch_ocr(self, paths: list[str]) -> dict[str, str]:
        import aiohttp

        to_fetch = [p for p in paths if p not in self._cache]
        if not to_fetch:
            return {p: self._cache[p] for p in paths}
        sem = asyncio.Semaphore(self.concurrency)
        async with aiohttp.ClientSession() as session:

            async def _one(p):
                async with sem:
                    return await self._ocr_one(p, session)

            await asyncio.gather(*[_one(p) for p in to_fetch])
        return {p: self._cache.get(p, "") for p in paths}
