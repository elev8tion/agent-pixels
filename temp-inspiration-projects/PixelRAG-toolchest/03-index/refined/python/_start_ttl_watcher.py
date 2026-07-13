def _start_ttl_watcher(self) -> None:
        """Start background thread that stops kiwix-serve after idle TTL."""
        if self._ttl_thread is not None and self._ttl_thread.is_alive():
            return

        def _watcher() -> None:
            while True:
                time.sleep(60)
                if not any(p is not None for p in self._procs):
                    break
                if time.time() - self._last_request_time > self._TTL_SECONDS:
                    logger.info(
                        "kiwix-serve idle > %ds, auto-stopping", self._TTL_SECONDS
                    )
                    self.stop()
                    break

        self._ttl_thread = threading.Thread(target=_watcher, daemon=True)
        self._ttl_thread.start()
