async def _capture_single(self, conn, wi, article, ac, page_h, nav_ms):
        """Single-tile article — same as sequential."""
        clip_h = min(TILE_HEIGHT, page_h)
        params = {
            "fromSurface": self.from_surface,
            "optimizeForSpeed": True,
            "clip": {
                "x": 0,
                "y": 0,
                "width": VIEWPORT_WIDTH,
                "height": clip_h,
                "scale": 1,
            },
        }
        raw_path = None
        if self.fmt == "raw":
            raw_path = f"/dev/shm/pixelrag_bench/w{wi}_{id(article)}_0.raw"
            params["rawFilePath"] = raw_path
        else:
            params["format"] = self.fmt
            if self.fmt == "jpeg":
                params["quality"] = self.quality

        t0 = time.monotonic()
        try:
            r = await conn.cdp("Page.captureScreenshot", params)
        except Exception as e:
            ac.errors.append(f"tile 0: {e}")
            return ac
        shot_ms = (time.monotonic() - t0) * 1000
        ac.total_shot_ms = shot_ms

        if "error" not in r:
            tc = TileCapture(
                shot_ms=shot_ms, nav_ms=nav_ms, tile_index=0, clip_y=0, clip_h=clip_h
            )
            if self.fmt == "raw":
                tc.raw_file_path = raw_path
            else:
                tc.image_bytes = base64.b64decode(r["result"]["data"])
            ac.tiles.append(tc)

        return ac
