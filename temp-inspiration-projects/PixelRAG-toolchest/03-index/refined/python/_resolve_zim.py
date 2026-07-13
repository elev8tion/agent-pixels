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
