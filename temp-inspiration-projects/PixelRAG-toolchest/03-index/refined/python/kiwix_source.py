class KiwixSource(Source):
    """Data source backed by a local Kiwix ZIM file served via kiwix-serve.

    Both article HTML and embedded images are served from the ZIM archive,
    eliminating all external network requests and Wikimedia rate-limiting.
    """

    _SKIP_PREFIXES = ("_assets_/", "-/", "_/", "_mw_/")
    _SKIP_EXACT = {"-", "mainpage"}

    # Well-known ZIM aliases → download URLs
    _ZIM_CATALOG = {
        "wikipedia-simple": "https://download.kiwix.org/zim/wikipedia/wikipedia_en_simple_all_nopic_2026-05.zim",
        "wikipedia-en": "https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2025-08.zim",
    }
    _DEFAULT_ZIM_DIR = Path.home() / ".cache" / "pixelrag" / "zim"

    def __init__(
        self,
        zim_path: str = "wikipedia-simple",
        kiwix_serve_url: str = "http://localhost:9454",
        book_name: Optional[str] = None,
        num_kiwix_instances: int = 8,
        **kwargs,
    ):
        self.zim_path = self._resolve_zim(zim_path)
        self._book_name = book_name
        self._article_paths: Optional[list[str]] = None
        self._zim = None
        self._redirect_ids: Optional[set[int]] = None
        from urllib.parse import urlparse

        parsed = urlparse(kiwix_serve_url)
        base_port = parsed.port or 9454
        self._serve_manager = KiwixServeManager(
            str(self.zim_path),
            base_port=base_port,
            num_instances=num_kiwix_instances,
        )
        _active_sources.append(self)

    @classmethod
    def _resolve_zim(cls, zim_path: str) -> Path:
        """Resolve a ZIM path: file path, alias, or URL. Downloads if needed."""
        # 1. Existing file
        p = Path(zim_path).expanduser().resolve()
        if p.exists():
            return p

        # 2. Known alias (e.g. "wikipedia-simple")
        if zim_path in cls._ZIM_CATALOG:
            url = cls._ZIM_CATALOG[zim_path]
            filename = url.rsplit("/", 1)[-1]
            dest = cls._DEFAULT_ZIM_DIR / filename
            if dest.exists():
                logger.info("Using cached ZIM: %s", dest)
                return dest
            return cls._download_zim(url, dest)

        # 3. URL
        if zim_path.startswith("http://") or zim_path.startswith("https://"):
            filename = zim_path.rsplit("/", 1)[-1]
            dest = cls._DEFAULT_ZIM_DIR / filename
            if dest.exists():
                logger.info("Using cached ZIM: %s", dest)
                return dest
            return cls._download_zim(zim_path, dest)

        raise FileNotFoundError(
            f"ZIM not found: {zim_path}\n"
            f"Pass a file path, URL, or alias: {', '.join(cls._ZIM_CATALOG.keys())}"
        )

    @staticmethod
    def _download_zim(url: str, dest: Path) -> Path:
        import urllib.request

        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(".zim.part")
        logger.info("Downloading: %s", url)

        resp = urllib.request.urlopen(url)
        total = int(resp.headers.get("Content-Length", 0))

        from tqdm import tqdm

        with (
            open(tmp, "wb") as f,
            tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=dest.name,
                ncols=80,
            ) as bar,
        ):
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
                bar.update(len(chunk))

        tmp.rename(dest)
        logger.info("Saved: %s (%.0f MB)", dest, dest.stat().st_size / 1e6)
        return dest

    def _get_zim(self):
        if self._zim is None:
            from libzim.reader import Archive

            self._zim = Archive(str(self.zim_path))
        return self._zim

    @property
    def book_name(self) -> str:
        if self._book_name is None:
            self._book_name = self.zim_path.stem
        return self._book_name

    def _is_article_path(self, path: str) -> bool:
        if not path:
            return False
        if any(path.startswith(p) for p in self._SKIP_PREFIXES):
            return False
        if path in self._SKIP_EXACT:
            return False
        if "." in path.rsplit("/", 1)[-1]:
            last_part = path.rsplit("/", 1)[-1]
            ext = last_part.rsplit(".", 1)[-1].lower()
            if ext in {
                "png",
                "jpg",
                "jpeg",
                "gif",
                "svg",
                "webp",
                "ico",
                "css",
                "js",
                "json",
                "woff",
                "woff2",
                "ttf",
                "eot",
                "tif",
                "tiff",
                "bmp",
                "mp3",
                "mp4",
                "ogg",
                "ogv",
                "webm",
                "flac",
                "wav",
                "opus",
                "mid",
            }:
                return False
        return True

    def _cache_path(self) -> Path:
        return Path(str(self.zim_path) + ".articles.json")

    def _load_article_cache(self) -> Optional[list[str]]:
        cache = self._cache_path()
        if not cache.exists():
            return None
        try:
            with open(cache, "r") as f:
                paths = json.load(f)
            logger.info("Loaded %d articles from cache %s", len(paths), cache)
            return paths
        except Exception as e:
            logger.warning("Failed to load article cache: %s", e)
            return None

    def _save_article_cache(self, paths: list[str]) -> None:
        cache = self._cache_path()
        tmp = cache.with_suffix(".tmp")
        try:
            with open(tmp, "w") as f:
                json.dump(paths, f)
            os.replace(tmp, cache)
            logger.info("Saved article cache (%d paths) to %s", len(paths), cache)
        except Exception as e:
            logger.warning("Failed to save article cache: %s", e)

    def _redirects_cache_path(self) -> Path:
        return Path(str(self.zim_path) + ".redirects.json")

    def _build_redirect_map(self) -> dict[str, str]:
        """Scan articles for client-side redirects not flagged by ZIM.

        Client-side redirects are tiny HTML pages (<1024 bytes) with
        ``<meta http-equiv="refresh" content="0;URL='./Target_Page'">``.
        Cached to ``<zim_path>.redirects.json``.
        """
        cache = self._redirects_cache_path()
        if cache.exists():
            try:
                with open(cache, "r") as f:
                    redirects = json.load(f)
                logger.info("Loaded %d redirects from cache %s", len(redirects), cache)
                return redirects
            except Exception as e:
                logger.warning("Failed to load redirects cache: %s", e)

        paths = self._build_article_list()
        zim = self._get_zim()
        redirects: dict[str, str] = {}
        url_re = re.compile(
            rb"""content\s*=\s*["'][^"']*URL\s*=\s*['"]?([^"'\s>]+)""", re.IGNORECASE
        )

        logger.info("Scanning %d articles for client-side redirects...", len(paths))
        for i, path in enumerate(paths):
            try:
                entry = zim.get_entry_by_path(path)
                item = entry.get_item()
                if item.size > 1024:
                    continue
                content = bytes(item.content)
                if b"http-equiv" not in content or b"refresh" not in content:
                    continue
                m = url_re.search(content)
                if m:
                    target = m.group(1).decode("utf-8", errors="replace")
                    target = target.lstrip("./")
                    if "#" in target:
                        target = target.split("#", 1)[0]
                    redirects[str(i)] = target
            except Exception:
                continue
            if i % 1_000_000 == 0 and i > 0:
                logger.info(
                    "  Scanned %dM / %dM, %d redirects so far",
                    i // 1_000_000,
                    len(paths) // 1_000_000,
                    len(redirects),
                )

        logger.info(
            "Found %d client-side redirects (%.1f%%)",
            len(redirects),
            100 * len(redirects) / max(len(paths), 1),
        )

        tmp = cache.with_suffix(".tmp")
        try:
            with open(tmp, "w") as f:
                json.dump(redirects, f)
            os.replace(tmp, cache)
            logger.info("Saved redirects cache to %s", cache)
        except Exception as e:
            logger.warning("Failed to save redirects cache: %s", e)

        return redirects

    def _load_redirect_set(self) -> set[int]:
        if self._redirect_ids is not None:
            return self._redirect_ids
        redirects = self._build_redirect_map()
        self._redirect_ids = {int(k) for k in redirects}
        return self._redirect_ids

    def _build_article_list(self) -> list[str]:
        if self._article_paths is not None:
            return self._article_paths
        cached = self._load_article_cache()
        if cached is not None:
            self._article_paths = cached
            return self._article_paths
        zim = self._get_zim()
        logger.info("Building article list from ZIM (%d entries)...", zim.entry_count)
        paths = []
        for i in range(zim.entry_count):
            try:
                entry = zim._get_entry_by_id(i)
                path = entry.path
                if self._is_article_path(path):
                    if not entry.is_redirect:
                        paths.append(path)
            except Exception:
                continue
            if i % 1_000_000 == 0 and i > 0:
                logger.info(
                    "  Scanned %dM / %dM entries, %d articles so far",
                    i // 1_000_000,
                    zim.entry_count // 1_000_000,
                    len(paths),
                )
        self._article_paths = paths
        logger.info("Found %d articles in ZIM", len(paths))
        self._save_article_cache(paths)
        return self._article_paths

    def _path_to_url(self, path: str, base_url: str) -> str:
        """Convert ZIM entry path to kiwix-serve URL with given base."""
        safe_chars = "/:@!$&'()*+,;="
        return f"{base_url}/content/{self.book_name}/{quote(path, safe=safe_chars)}"

    def __iter__(self) -> Iterator[Document]:
        paths = self._build_article_list()
        self._serve_manager.ensure_running()
        redirect_ids = self._load_redirect_set()
        health_interval = 1_000
        yielded = 0
        for i, path in enumerate(paths):
            if i in redirect_ids:
                continue
            title = path.replace("_", " ")
            base_url = self._serve_manager.next_url()
            yield Document(
                id=str(i),
                url=self._path_to_url(path, base_url),
                metadata={"title": title, "type": "kiwix"},
            )
            yielded += 1
            if yielded % health_interval == 0:
                self._serve_manager.ensure_running()

    def __len__(self) -> int:
        return len(self._build_article_list())

    def close(self) -> None:
        self._serve_manager.stop()
        if self in _active_sources:
            _active_sources.remove(self)

    def __del__(self) -> None:
        self.close()

    def __enter__(self) -> "KiwixSource":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
