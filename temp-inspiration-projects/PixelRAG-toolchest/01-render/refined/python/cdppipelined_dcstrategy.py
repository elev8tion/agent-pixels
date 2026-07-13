@dataclass
class CDPPipelinedDCStrategy:
    chrome_path: str
    n_workers: int
    fmt: str = "jpeg"
    quality: int = 85
    headless_shell: bool = False

    _connections: list = None
    _base_port: int = 9300

    @property
    def name(self) -> str:
        return f"{self.n_workers}w {self.fmt} pipedc"

    @property
    def from_surface(self) -> bool:
        return True

    @property
    def launcher(self) -> str:
        return "websocket"

    async def setup(self) -> None:
        self._connections = []
        for i in range(self.n_workers):
            conn = await launch_two_tab(
                self.chrome_path,
                self._base_port + i,
                headless_shell=self.headless_shell,
            )
            self._connections.append(conn)

        for conn in self._connections:
            for tab in [conn.tab_a, conn.tab_b]:
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
        if self._connections:
            for conn in self._connections:
                await conn.close()

    async def capture_articles(self, articles: list[dict]) -> list[ArticleCapture]:
        n = len(self._connections)
        wp = [[] for _ in range(n)]
        article_index = {a["path"]: i for i, a in enumerate(articles)}
        for i, a in enumerate(articles):
            wp[i % n].append(a)

        all_results = [None] * len(articles)

        async def worker_task(wi):
            for ac in self._pipeline_worker(wi, wp[wi]):
                ac_result = await ac
                all_results[article_index[ac_result.article_path]] = ac_result

        async def worker_task(wi):  # noqa: F811
            arts = wp[wi]
            conn = self._connections[wi]
            tabs = [conn.tab_a, conn.tab_b]

            for i, article in enumerate(arts):
                tab = tabs[i % 2]
                other = tabs[(i + 1) % 2]

                nav_task = self._navigate(tab, article)
                if i > 0:
                    cap_task = self._capture(other, prev_article, prev_page_h, wi)  # noqa: F821
                    nav_result, cap_result = await asyncio.gather(nav_task, cap_task)
                    all_results[article_index[prev_article["path"]]] = cap_result  # noqa: F821
                else:
                    nav_result = await nav_task

                prev_article = article
                prev_page_h = nav_result

            last_tab = tabs[len(arts) % 2 - 1] if arts else tabs[0]
            if arts:
                last_tab = tabs[(len(arts) - 1) % 2]
                cap_result = await self._capture(
                    last_tab, prev_article, prev_page_h, wi
                )
                all_results[article_index[prev_article["path"]]] = cap_result

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
            page_h = r["result"]["result"]["value"]
        except Exception:
            page_h = TILE_HEIGHT

        return max(page_h, 1)

    async def _capture(
        self, tab, article: dict, page_h: int, wi: int
    ) -> ArticleCapture:
        ac = ArticleCapture(article_path=article["path"])
        ac.page_height = page_h
        n_tiles = max(1, (page_h + TILE_HEIGHT - 1) // TILE_HEIGHT)
        ac.n_tiles_expected = n_tiles

        for t in range(n_tiles):
            clip_h = min(TILE_HEIGHT, page_h - t * TILE_HEIGHT)
            if clip_h <= 28:
                break

            if t > 0:
                try:
                    await tab.cdp(
                        "Runtime.evaluate",
                        {
                            "expression": f"""new Promise(resolve => {{
                            window.scrollTo(0, {t * TILE_HEIGHT});
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
                "directClip": True,
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
