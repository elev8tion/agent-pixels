async def teardown(self) -> None:
        if self._connections:
            for conn in self._connections:
                await conn.close()
            self._connections = None
