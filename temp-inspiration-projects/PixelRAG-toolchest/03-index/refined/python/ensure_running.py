def ensure_running(self) -> None:
        """Ensure all instances are running, restart any that crashed."""
        self.touch()
        for idx in range(self.num_instances):
            port = self.ports[idx]
            proc = self._procs[idx]
            alive = proc is not None and proc.poll() is None
            if alive and self._health_check(port):
                continue
            if proc is not None:
                logger.warning(
                    "kiwix-serve instance %d (pid %s, port %d) is dead, restarting...",
                    idx,
                    proc.pid,
                    port,
                )
            self._start_instance(idx)
