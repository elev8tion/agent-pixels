@dataclass
class CDPOverlapStrategy:
    """2-tab overlapping nav+capture with semaphore-limited captures."""

    chrome_path: str
    n_workers: int
    capture_limit: int = 0
    fmt: str = "jpeg"
    quality: int = 85
    from_surface: bool = True
    launcher: str = "websocket"
    headless_shell: bool = False

    _tabs: list = None
    _procs: list = None
    _base_port: int = 9300
    _capture_sem: asyncio.Semaphore = None

    @property
    def name(self) -> str:
        cl = self.capture_limit or self.n_workers // 2
        return f"{self.n_workers}w-{cl}c overlap"

    async def setup(self) -> None:
        cl = self.capture_limit or self.n_workers // 2
        self._capture_sem = asyncio.Semaphore(cl)

        self._tabs = []
        self._procs = []
        for i in range(self.n_workers):
            tab_a, tab_b, proc = await _launch_two_tabs(
                self.chrome_path,
                self._base_port + i,
                headless_shell=self.headless_shell,
            )
            self._tabs.append((tab_a, tab_b))
            self._procs.append(proc)

        for tab_a, tab_b in self._tabs:
            for tab in [tab_a, tab_b]:
                await tab.cdp("Page.enable")
                await tab.cdp(
                    "Emulation.setDeviceMetricsOverride",
                    {
                        "width": VIEWPORT_WIDTH,
                        "height": TILE_HEIGHT,
                        "deviceScaleFactor": 1,
                        "mobile": False,
                    },
                )

        if self.fmt == "raw":
            os.makedirs("/dev/shm/pixelrag_bench", exist_ok=True)

    async def teardown(self) -> None:
        if self._tabs:
            for tab_a, tab_b in self._tabs:
                try:
                    await tab_a.close()
                except Exception:
                    pass
                try:
                    await tab_b._ws.close()
                except Exception:
                    pass
        if self._procs:
            for p in self._procs:
                try:
                    p.send_signal(signal.SIGTERM)
                    p.wait(timeout=3)
                except Exception:
                    try:
                        p.kill()
                    except Exception:
                        pass

    async def capture_articles(self, articles: list[dict]) -> list[ArticleCapture]:
        n = len(self._tabs)
        wp = [[] for _ in range(n)]
        article_index = {a["path"]: i for i, a in enumerate(articles)}
        for i, a in enumerate(articles):
            wp[i % n].append(a)

        all_results = [None] * len(articles)

        async def worker_task(wi):
            tab_a, tab_b = self._tabs[wi]
            arts = wp[wi]
            if not arts:
                return

            page_h = await self._navigate(tab_a, arts[0])

            for i in range(len(arts)):
                cur_tab = tab_a if i % 2 == 0 else tab_b
                nxt_tab = tab_b if i % 2 == 0 else tab_a

                if i + 1 < len(arts):
                    nav_task = asyncio.create_task(self._navigate(nxt_tab, arts[i + 1]))
                else:
                    nav_task = None

                ac = await self._capture(cur_tab, arts[i], page_h, wi)
                all_results[article_index[arts[i]["path"]]] = ac

                if nav_task:
                    page_h = await nav_task

        await asyncio.gather(
            *[worker_task(i) for i in range(n)], return_exceptions=True
        )
        return [r for r in all_results if r is not None]

    async def _navigate(self, tab, article: dict) -> int:
        try:
            await tab.cdp("Page.navigate", {"url": article_url(article)})
        except Exception:
            return TILE_HEIGHT

        try:
            r = await tab.cdp(
                "Runtime.evaluate",
                {
                    "expression": WAIT_FONTS_IMGS,
                    "awaitPromise": True,
                    "returnByValue": True,
                },
            )
            return max(r["result"]["result"]["value"], 1)
        except Exception:
            return TILE_HEIGHT

    async def _capture(
        self, tab, article: dict, page_h: int, wi: int
    ) -> ArticleCapture:
        ac = ArticleCapture(article_path=article["path"])
        ac.page_height = page_h
        n_tiles = max(1, (page_h + TILE_HEIGHT - 1) // TILE_HEIGHT)
        ac.n_tiles_expected = n_tiles

        async with self._capture_sem:
            for t in range(n_tiles):
                clip_h = min(TILE_HEIGHT, page_h - t * TILE_HEIGHT)
                if clip_h <= 28:
                    break

                if t > 0:
                    y = t * TILE_HEIGHT
                    try:
                        await tab.cdp(
                            "Runtime.evaluate",
                            {
                                "expression": f"""new Promise(resolve => {{
                                window.scrollTo(0, {y});
                                requestAnimationFrame(() => requestAnimationFrame(() => {{
                                    const imgs = Array.from(document.images).filter(i => {{
                                        if (i.complete) return false;
                                        const r = i.getBoundingClientRect();
                                        return r.bottom > 0 && r.top < window.innerHeight;
                                    }});
                                    if (imgs.length === 0) return resolve();
                                    const timeout = new Promise(r => setTimeout(r, 500));
                                    const loaded = Promise.all(imgs.map(i => new Promise(r => {{
                                        i.addEventListener('load', r, {{once: true}});
                                        i.addEventListener('error', r, {{once: true}});
                                    }})));
                                    Promise.race([loaded, timeout]).then(resolve);
                                }}));
                            }})""",
                                "awaitPromise": True,
                            },
                        )
                    except Exception:
                        pass

                params = {
                    "fromSurface": self.from_surface,
                    "optimizeForSpeed": True,
                    "clip": {
                        "x": 0,
                        "y": t * TILE_HEIGHT,
                        "width": VIEWPORT_WIDTH,
                        "height": clip_h,
                        "scale": 1,
                    },
                }

                raw_path = None
                if self.fmt == "raw":
                    raw_path = f"/dev/shm/pixelrag_bench/w{wi}_{id(article)}_{t}.raw"
                    params["rawFilePath"] = raw_path
                else:
                    params["format"] = self.fmt
                    if self.fmt == "jpeg":
                        params["quality"] = self.quality

                t0 = time.monotonic()
                try:
                    r = await tab.cdp("Page.captureScreenshot", params)
                except Exception as e:
                    ac.errors.append(f"tile {t}: {e}")
                    continue
                shot_ms = (time.monotonic() - t0) * 1000
                ac.total_shot_ms += shot_ms

                if "error" in r:
                    ac.errors.append(f"tile {t}: {r['error']}")
                    continue

                tc = TileCapture(
                    shot_ms=shot_ms,
                    nav_ms=0.0,
                    tile_index=t,
                    clip_y=t * TILE_HEIGHT,
                    clip_h=clip_h,
                )
                if self.fmt == "raw":
                    tc.raw_file_path = raw_path
                else:
                    tc.image_bytes = base64.b64decode(r["result"]["data"])
                ac.tiles.append(tc)

        return ac
