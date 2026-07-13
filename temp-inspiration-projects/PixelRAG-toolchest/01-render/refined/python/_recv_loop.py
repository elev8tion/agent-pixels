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
