def close(self) -> None:
        # Send shutdown sentinels. Workers read None from work_queue and exit.
        for _ in self.workers:
            try:
                self.work_queue.put(None)
            except Exception:
                pass
        # Soft-join: give each worker a short window to exit cleanly.
        for _gid, p in self.workers.items():
            p.join(timeout=10)
        # Force-kill any stragglers so interpreter shutdown isn't blocked on
        # non-daemon children. CUDA context teardown in child can hang
        # indefinitely; SIGTERM/SIGKILL is safe here because results already
        # landed in result_queue and partial_path files before close() runs.
        for gid, p in list(self.workers.items()):
            if p.is_alive():
                logger.warning(
                    "GPU %d worker pid=%s didn't exit on sentinel, SIGTERM", gid, p.pid
                )
                p.terminate()
                p.join(timeout=5)
            if p.is_alive():
                logger.error(
                    "GPU %d worker pid=%s ignored SIGTERM, SIGKILL", gid, p.pid
                )
                p.kill()
                p.join(timeout=5)
        # Drop queue background feeder threads so they don't block atexit.
        for q in (self.work_queue, self.result_queue):
            try:
                q.close()
                q.cancel_join_thread()
            except Exception:
                pass
