def next_url(self) -> str:
        """Return base URL for the next instance (round-robin).

        Resets idle timer. If the selected instance is unresponsive, try
        to restart it and fall back to other healthy instances.
        """
        for _ in range(self.num_instances):
            idx = next(self._port_cycle)
            port = self.ports[idx]
            if self._health_check(port):
                return f"http://localhost:{port}"
            logger.warning("kiwix-serve on port %d unresponsive, restarting...", port)
            try:
                self._start_instance(idx)
                return f"http://localhost:{port}"
            except RuntimeError:
                logger.error("Failed to restart kiwix-serve on port %d, skipping", port)
        logger.error(
            "All kiwix-serve instances down, falling back to port %d", self.base_port
        )
        return f"http://localhost:{self.base_port}"
