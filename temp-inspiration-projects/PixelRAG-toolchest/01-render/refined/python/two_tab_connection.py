class TwoTabConnection:
    """Chrome process with two tabs, each independently controllable."""

    def __init__(self, ws_a, ws_b, proc):
        self.tab_a = ws_a
        self.tab_b = ws_b
        self._proc = proc

    async def close(self):
        try:
            await self.tab_a.close()
        except Exception:
            pass
        try:
            await self.tab_b.close()
        except Exception:
            pass
