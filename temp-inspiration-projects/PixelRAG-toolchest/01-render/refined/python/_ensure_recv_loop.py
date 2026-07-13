def _ensure_recv_loop(self):
        if self._recv_task is None or self._recv_task.done():
            loop = asyncio.get_event_loop()
            self._recv_task = loop.create_task(self._recv_loop())
