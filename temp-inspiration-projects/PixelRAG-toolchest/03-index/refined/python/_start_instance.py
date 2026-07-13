def _start_instance(self, idx: int) -> None:
        """Start or restart a single kiwix-serve instance."""
        port = self.ports[idx]
        old = self._procs[idx]
        if old is not None:
            self._kill_proc(old)
            self._procs[idx] = None

        if self._health_check(port):
            logger.info("kiwix-serve already running on port %d (external)", port)
            return

        logger.info(
            "Starting kiwix-serve instance %d on port %d (threads=%d) ...",
            idx,
            port,
            self.threads_per_instance,
        )
        proc = subprocess.Popen(
            [
                self._binary,
                "--port",
                str(port),
                "--threads",
                str(self.threads_per_instance),
                self.zim_path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setpgrp,
        )
        for _ in range(30):
            time.sleep(1)
            if self._health_check(port):
                logger.info(
                    "kiwix-serve instance %d started (pid %d, port %d)",
                    idx,
                    proc.pid,
                    port,
                )
                self._procs[idx] = proc
                self._start_ttl_watcher()
                return
        raise RuntimeError(
            f"kiwix-serve failed to start on port {port} (pid {proc.pid})"
        )
