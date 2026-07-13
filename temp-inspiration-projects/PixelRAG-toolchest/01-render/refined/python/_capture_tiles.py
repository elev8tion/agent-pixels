async def _capture_tiles(
        self, conn, wi: int, article: dict, page_h: int
    ) -> ArticleCapture:
        """Phase 2: Pure capture, no waiting."""
        ac = ArticleCapture(article_path=article["path"])
        ac.page_height = page_h
        n_tiles = max(1, (page_h + TILE_HEIGHT - 1) // TILE_HEIGHT)
        ac.n_tiles_expected = n_tiles

        t0 = time.monotonic()
        for t in range(n_tiles):
            clip_h = min(TILE_HEIGHT, page_h - t * TILE_HEIGHT)
            if clip_h <= 28:
                break

            if t > 0:
                await conn.cdp(
                    "Runtime.evaluate",
                    {"expression": f"window.scrollTo(0, {t * TILE_HEIGHT})"},
                )
                await conn.cdp(
                    "Runtime.evaluate",
                    {
                        "expression": "new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))",
                        "awaitPromise": True,
                    },
                )

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

            try:
                r = await conn.cdp("Page.captureScreenshot", params)
            except Exception as e:
                ac.errors.append(f"tile {t}: {e}")
                continue

            shot_ms = (time.monotonic() - t0) * 1000 / (t + 1)

            if "error" in r:
                ac.errors.append(f"tile {t}: {r['error']}")
                continue

            tc = TileCapture(
                shot_ms=shot_ms,
                tile_index=t,
                clip_y=t * TILE_HEIGHT,
                clip_h=clip_h,
            )
            if self.fmt == "raw":
                tc.raw_file_path = raw_path
            else:
                tc.image_bytes = base64.b64decode(r["result"]["data"])
            ac.tiles.append(tc)

        ac.total_shot_ms = (time.monotonic() - t0) * 1000
        return ac
