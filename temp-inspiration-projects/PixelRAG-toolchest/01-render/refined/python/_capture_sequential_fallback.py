async def _capture_sequential_fallback(self, conn, wi, article, ac, page_h, nav_ms):
        """Playwright doesn't expose raw websocket — fall back to sequential."""
        n_tiles = max(1, (page_h + TILE_HEIGHT - 1) // TILE_HEIGHT)
        for t in range(n_tiles):
            clip_h = min(TILE_HEIGHT, page_h - t * TILE_HEIGHT)
            if clip_h <= 28:
                break
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
            if self.fmt == "raw":
                raw_path = f"/dev/shm/pixelrag_bench/w{wi}_{id(article)}_{t}.raw"
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

            if "error" not in r:
                tc = TileCapture(
                    shot_ms=shot_ms,
                    nav_ms=nav_ms if t == 0 else 0.0,
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
