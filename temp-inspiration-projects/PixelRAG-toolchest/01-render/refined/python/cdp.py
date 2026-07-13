async def cdp(self, method: str, params: dict | None = None) -> dict:
        result = await self._cdp.send(method, params or {})
        return {"result": result}
