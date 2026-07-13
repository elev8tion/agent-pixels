async def _capture_article(
        self, conn, article: dict, ac: ArticleCapture, th: int
    ) -> None:
        """Navigate, wait for render, capture all tiles.  Mutates ac in place."""
        # === Configure viewport ===
        try:
            await conn.cdp("Page.enable")
            await conn.cdp(
                "Emulation.setDeviceMetricsOverride",
                {
                    "width": VIEWPORT_WIDTH,
                    "height": th,
                    "deviceScaleFactor": 1,
                    "mobile": False,
                },
            )
        except Exception as e:
            ac.errors.append(f"setup cdp: {e}")
            return

        # === Navigate ===
        t_nav = time.monotonic()
        target_url = article_url(article)

        # Use Page.frameStoppedLoading: reliable with --in-process-gpu
        # (Page.frameNavigated has a Chrome bug where it's sometimes not fired).
        nav_event_fut = asyncio.ensure_future(
            conn.wait_for_event("Page.frameStoppedLoading", timeout=30.0)
        )
        try:
            await conn.cdp("Page.navigate", {"url": target_url})
        except Exception as e:
            nav_event_fut.cancel()
            ac.errors.append(f"nav: {e}")
            return

        try:
            await nav_event_fut
        except asyncio.TimeoutError:
            ac.errors.append("nav: frameStoppedLoading timeout (30s)")
            return
        except Exception as e:
            ac.errors.append(f"nav: frameStoppedLoading wait error: {e}")
            return

        # === Wait for fonts + images, measure page height ===
        try:
            wait_expr = WAIT_FONTS_IMGS.replace(
                "setTimeout(r, 2000)", f"setTimeout(r, {self.nav_timeout_ms})"
            )
            r = await conn.cdp(
                "Runtime.evaluate",
                {
                    "expression": wait_expr,
                    "awaitPromise": True,
                    "returnByValue": True,
                },
            )
            page_h = r["result"]["result"]["value"]
        except Exception:
            page_h = th

        if page_h <= 0:
            page_h = th

        nav_ms = (time.monotonic() - t_nav) * 1000
        ac.total_nav_ms = nav_ms
        ac.page_height = page_h
        n_tiles = max(1, (page_h + th - 1) // th)
        ac.n_tiles_expected = n_tiles

        # === Capture tiles ===
        for t in range(n_tiles):
            clip_y = t * th
            clip_h = min(th, page_h - clip_y)
            if clip_h <= 28:
                break

            # Scroll into position and wait for viewport images.
            try:
                await conn.cdp(
                    "Runtime.evaluate",
                    {
                        "expression": f"""new Promise(resolve => {{
                        window.scrollTo(0, {clip_y});
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
                    "y": clip_y,
                    "width": VIEWPORT_WIDTH,
                    "height": clip_h,
                    "scale": 1,
                },
            }

            raw_path = None
            if self.fmt == "raw":
                raw_path = (
                    f"/dev/shm/pixelrag_bench"
                    f"/os_{article['path'].replace('/', '_')}_{t}.raw"
                )
                params["rawFilePath"] = raw_path
            else:
                params["format"] = self.fmt
                if self.fmt == "jpeg":
                    params["quality"] = self.quality

            t0 = time.monotonic()
            try:
                r = await conn.cdp("Page.captureScreenshot", params)
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
                nav_ms=nav_ms if t == 0 else 0.0,
                tile_index=t,
                clip_y=clip_y,
                clip_h=clip_h,
            )
            if self.fmt == "raw":
                tc.raw_file_path = raw_path
            else:
                tc.image_bytes = base64.b64decode(r["result"]["data"])
            ac.tiles.append(tc)
