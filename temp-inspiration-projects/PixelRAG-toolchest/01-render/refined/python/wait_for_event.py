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
