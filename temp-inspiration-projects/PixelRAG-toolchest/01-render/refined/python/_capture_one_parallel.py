async def _capture_one_parallel(self, wi: int, article: dict) -> ArticleCapture:
        conn = self._connections[wi]
        ac = ArticleCapture(article_path=article["path"])

        t_nav = time.monotonic()
        try:
            await conn.cdp("Page.navigate", {"url": article_url(article)})
        except Exception as e:
            ac.errors.append(f"nav: {e}")
            return ac
        await asyncio.sleep(0.03)
        nav_ms = (time.monotonic() - t_nav) * 1000
        ac.total_nav_ms = nav_ms

        try:
            r = await conn.cdp(
                "Runtime.evaluate",
                {"expression": "document.documentElement.scrollHeight"},
            )
            page_h = r["result"]["result"]["value"]
        except Exception:
            page_h = TILE_HEIGHT

        ac.page_height = page_h
        n_tiles = max(1, (page_h + TILE_HEIGHT - 1) // TILE_HEIGHT)
        ac.n_tiles_expected = n_tiles

        if n_tiles <= 1:
            # Single tile — same as sequential
            return await self._capture_single(conn, wi, article, ac, page_h, nav_ms)

        # Fire all tile requests at once
        # Need raw websocket access for parallel sends
        if not hasattr(conn, "_ws"):
            # Playwright connection — fall back to sequential
            return await self._capture_sequential_fallback(
                conn, wi, article, ac, page_h, nav_ms
            )

        ws = conn._ws
        pending = []
        t0 = time.monotonic()

        for t in range(n_tiles):
            clip_h = min(TILE_HEIGHT, page_h - t * TILE_HEIGHT)
            if clip_h <= 28:
                break

            conn._msg_id += 1
            mid = conn._msg_id

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

            await ws.send(
                json.dumps(
                    {
                        "id": mid,
                        "method": "Page.captureScreenshot",
                        "params": params,
                    }
                )
            )
            pending.append((mid, t, clip_h, raw_path))

        # Collect all responses
        mid_to_info = {mid: (t, clip_h, rp) for mid, t, clip_h, rp in pending}
        collected = {}
        while len(collected) < len(pending):
            try:
                r = json.loads(await asyncio.wait_for(ws.recv(), timeout=180))
                rid = r.get("id")
                if rid in mid_to_info:
                    collected[rid] = r
            except Exception as e:
                ac.errors.append(f"recv: {e}")
                break

        total_shot_ms = (time.monotonic() - t0) * 1000
        ac.total_shot_ms = total_shot_ms

        # Decode in tile order
        for mid, t, clip_h, raw_path in pending:
            r = collected.get(mid)
            if not r or "error" in r:
                ac.errors.append(f"tile {t}: {r.get('error') if r else 'no response'}")
                continue

            tc = TileCapture(
                shot_ms=total_shot_ms / len(pending),
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
