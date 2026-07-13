class KiwixServeManager:
    """Manages multiple kiwix-serve processes for high-concurrency serving.

    Benchmark results (80 concurrent requests, 2000 articles):
        1x --threads 4:   454 rps, p50=160ms
        2x --threads 4:   720 rps, p50=98ms
        4x --threads 4:  1212 rps, p50=21ms
        8x --threads 4:  2011 rps, p50=20ms

    Multi-process scales linearly because each instance independently
    decompresses ZIM clusters without lock contention.
    """

    _SEARCH_PATHS = (
        str(Path(__file__).resolve().parents[4] / ".local" / "bin" / "kiwix-serve"),
        "/usr/bin/kiwix-serve",
        "/usr/local/bin/kiwix-serve",
    )

    def __init__(
        self,
        zim_path: str,
        base_port: int = 9454,
        num_instances: int = 8,
        threads_per_instance: int = 4,
    ):
        self.zim_path = zim_path
        self.base_port = base_port
        self.num_instances = num_instances
        self.threads_per_instance = threads_per_instance
        self._procs: list[Optional[subprocess.Popen]] = [None] * num_instances
        self._binary = self._find_binary()
        self._port_cycle = itertools.cycle(range(num_instances))
        self._last_request_time = time.time()
        self._ttl_thread: threading.Thread | None = None

    @property
    def ports(self) -> list[int]:
        return [self.base_port + i for i in range(self.num_instances)]

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

    _KIWIX_TOOLS_VERSION = "3.7.0-2"

    def _find_binary(self) -> str:
        for p in self._SEARCH_PATHS:
            if os.path.isfile(p) and os.access(p, os.X_OK):
                return p
        found = shutil.which("kiwix-serve")
        if found:
            return found
        return self._install_kiwix_tools()

    def _install_kiwix_tools(self) -> str:
        """Auto-download kiwix-tools binary."""
        import platform
        import tarfile
        import tempfile
        import urllib.request

        arch = (
            "x86_64"
            if platform.machine() in ("x86_64", "AMD64")
            else platform.machine()
        )
        url = (
            f"https://download.kiwix.org/release/kiwix-tools/"
            f"kiwix-tools_linux-{arch}-{self._KIWIX_TOOLS_VERSION}.tar.gz"
        )

        install_dir = Path(self._SEARCH_PATHS[0]).parent
        install_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Downloading kiwix-tools %s...", self._KIWIX_TOOLS_VERSION)
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
            urllib.request.urlretrieve(url, tmp.name)
            with tarfile.open(tmp.name) as tar:
                for member in tar.getmembers():
                    if member.name.endswith("kiwix-serve"):
                        member.name = "kiwix-serve"
                        tar.extract(member, install_dir)
                    elif member.name.endswith("kiwix-manage"):
                        member.name = "kiwix-manage"
                        tar.extract(member, install_dir)
            os.unlink(tmp.name)

        binary = str(install_dir / "kiwix-serve")
        os.chmod(binary, 0o755)
        logger.info("Installed kiwix-serve to %s", binary)
        return binary

    def _health_check(self, port: int) -> bool:
        """Quick HTTP check to see if kiwix-serve is responding."""
        import urllib.request

        try:
            req = urllib.request.Request(f"http://localhost:{port}/", method="HEAD")
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception:
            return False

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

    _TTL_SECONDS = 300  # 5 min idle → auto-stop

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

    def touch(self) -> None:
        """Reset the idle timer."""
        self._last_request_time = time.time()

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

    def _kill_proc(self, proc: subprocess.Popen) -> None:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except (OSError, ProcessLookupError):
            pass
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (OSError, ProcessLookupError):
                pass

    def stop(self) -> None:
        for idx, proc in enumerate(self._procs):
            if proc is not None:
                self._kill_proc(proc)
                self._procs[idx] = None

    def __del__(self) -> None:
        self.stop()
