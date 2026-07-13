def stop(self) -> None:
        for idx, proc in enumerate(self._procs):
            if proc is not None:
                self._kill_proc(proc)
                self._procs[idx] = None
