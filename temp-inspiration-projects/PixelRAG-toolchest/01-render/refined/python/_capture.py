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
