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
