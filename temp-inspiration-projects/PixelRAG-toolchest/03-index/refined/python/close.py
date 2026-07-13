def close(self) -> None:
        self._serve_manager.stop()
        if self in _active_sources:
            _active_sources.remove(self)
