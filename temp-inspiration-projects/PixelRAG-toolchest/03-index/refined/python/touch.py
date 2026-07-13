def touch(self) -> None:
        """Reset the idle timer."""
        self._last_request_time = time.time()
