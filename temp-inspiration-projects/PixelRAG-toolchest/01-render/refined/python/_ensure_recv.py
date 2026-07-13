def _ensure_recv(self):
        if self._recv_task is None or self._recv_task.done():
            self._recv_task = asyncio.get_event_loop().create_task(self._recv_loop())
