class WebsocketConnection:
    """Direct websocket CDP connection."""

    def __init__(self, ws, proc):
        self._ws = ws
        self._proc = proc
        self._msg_id = 0
        # Pending response futures keyed by message id.
        self._pending: dict[int, asyncio.Future] = {}
        # Listeners for CDP events keyed by method name; each value is a list
        # of (Future, filter_fn) pairs.  filter_fn receives the event params
        # dict and should return True to resolve the future.
        self._event_listeners: dict[str, list] = {}
        self._recv_task: asyncio.Task | None = None

    # ------------------------------------------------------------------
    # Internal receive loop — started lazily on first use.
    # ------------------------------------------------------------------

    def _ensure_recv_loop(self):
        if self._recv_task is None or self._recv_task.done():
            loop = asyncio.get_event_loop()
            self._recv_task = loop.create_task(self._recv_loop())

    async def _recv_loop(self):
        try:
            async for raw in self._ws:
                msg = json.loads(raw)
                msg_id = msg.get("id")
                if msg_id is not None:
                    # Response to a command.
                    fut = self._pending.pop(msg_id, None)
                    if fut and not fut.done():
                        fut.set_result(msg)
                else:
                    # Event notification.
                    method = msg.get("method", "")
                    listeners = self._event_listeners.get(method, [])
                    remaining = []
                    for fut, filter_fn in listeners:
                        if fut.done():
                            continue
                        params = msg.get("params", {})
                        try:
                            matched = filter_fn(params) if filter_fn else True
                        except Exception:
                            matched = True
                        if matched:
                            fut.set_result(params)
                        else:
                            remaining.append((fut, filter_fn))
                    if remaining:
                        self._event_listeners[method] = remaining
                    elif listeners:
                        # All listeners matched or were done — clean up
                        # the stale list so it doesn't accumulate entries.
                        self._event_listeners.pop(method, None)
        except Exception:
            # Socket closed or error — resolve all pending futures with an
            # exception so callers don't hang.
            exc = ConnectionError("WebSocket receive loop ended")
            for fut in self._pending.values():
                if not fut.done():
                    fut.set_exception(exc)
            for listeners in self._event_listeners.values():
                for fut, _ in listeners:
                    if not fut.done():
                        fut.set_exception(exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def cdp(self, method: str, params: dict | None = None) -> dict:
        self._ensure_recv_loop()
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
        self,
        method: str,
        timeout: float = 30.0,
        filter_fn=None,
    ) -> dict:
        """Wait for a CDP event with the given method name.

        Args:
            method: CDP event method, e.g. "Page.frameStoppedLoading".
                    NOTE: Prefer Page.frameStoppedLoading over
                    Page.frameNavigated for navigation waits — Chrome has a
                    bug with --in-process-gpu where Page.frameNavigated is
                    sometimes never fired when many instances navigate
                    concurrently.
            timeout: Seconds to wait before raising asyncio.TimeoutError.
            filter_fn: Optional callable(params) -> bool.  The future is
                       resolved only when filter_fn returns True.  If None,
                       the first matching event resolves the future.

        Returns:
            The event ``params`` dict.
        """
        self._ensure_recv_loop()
        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        self._event_listeners.setdefault(method, []).append((fut, filter_fn))
        try:
            return await asyncio.wait_for(asyncio.shield(fut), timeout=timeout)
        except asyncio.TimeoutError:
            # Remove the stale listener.
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
