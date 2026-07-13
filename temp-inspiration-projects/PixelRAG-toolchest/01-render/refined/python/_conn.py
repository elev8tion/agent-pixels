class _Conn:
    """Minimal CDP connection with a receive loop."""

    def __init__(self, ws, proc, user_data_dir=None):
        self._ws = ws
        self._proc = proc
        self._user_data_dir = user_data_dir
        self._msg_id = 0
        self._pending: dict[int, asyncio.Future] = {}
        self._event_listeners: dict[str, list] = {}
        self._recv_task: asyncio.Task | None = None

    def _ensure_recv(self):
        if self._recv_task is None or self._recv_task.done():
            self._recv_task = asyncio.get_event_loop().create_task(self._recv_loop())

    async def _recv_loop(self):
        try:
            async for raw in self._ws:
                msg = json.loads(raw)
                mid = msg.get("id")
                if mid is not None:
                    fut = self._pending.pop(mid, None)
                    if fut and not fut.done():
                        fut.set_result(msg)
                else:
                    method = msg.get("method", "")
                    listeners = self._event_listeners.get(method, [])
                    remaining = []
                    for fut, filter_fn in listeners:
                        if fut.done():
                            continue
                        params = msg.get("params", {})
                        matched = filter_fn(params) if filter_fn else True
                        if matched:
                            fut.set_result(params)
                        else:
                            remaining.append((fut, filter_fn))
                    self._event_listeners[method] = remaining
        except Exception:
            exc = ConnectionError("WebSocket receive loop ended")
            for fut in self._pending.values():
                if not fut.done():
                    fut.set_exception(exc)
            for listeners in self._event_listeners.values():
                for fut, _ in listeners:
                    if not fut.done():
                        fut.set_exception(exc)

    async def cdp(self, method: str, params: dict | None = None) -> dict:
        self._ensure_recv()
        self._msg_id += 1
        mid = self._msg_id
        msg = {"id": mid, "method": method}
        if params:
            msg["params"] = params
        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        self._pending[mid] = fut
        await self._ws.send(json.dumps(msg))
        return await asyncio.wait_for(fut, timeout=180)

    async def wait_for_event(
        self, method: str, timeout: float = 30.0, filter_fn=None
    ) -> dict:
        self._ensure_recv()
        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        self._event_listeners.setdefault(method, []).append((fut, filter_fn))
        try:
            return await asyncio.wait_for(asyncio.shield(fut), timeout=timeout)
        except asyncio.TimeoutError:
            listeners = self._event_listeners.get(method, [])
            self._event_listeners[method] = [
                (f, fn) for f, fn in listeners if f is not fut
            ]
            if not fut.done():
                fut.cancel()
            raise

    async def close(self):
        try:
            await self._ws.close()
        except Exception:
            pass
        self._proc.send_signal(signal.SIGTERM)
        try:
            self._proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._proc.kill()
        if self._user_data_dir:
            shutil.rmtree(self._user_data_dir, ignore_errors=True)
