async def capture_url(
    ws,
    msg_id_ref: list,
    url: str,
    tile_dir: Path,
    *,
    tile_h: int = 8192,
    quality: int = 85,
    viewport_w: int = VIEWPORT_W,
    image_format: str = "jpeg",
    from_surface: bool = True,
    wait_network_idle: bool = False,
) -> int:
    """Capture a URL as tiled images via direct CDP websocket.

    Returns the number of tiles written.
    """
    tile_dir.mkdir(parents=True, exist_ok=True)

    await _cdp_send(ws, msg_id_ref, "Page.navigate", {"url": url})

    # Wait for load (+ optional network-idle) + fonts + layout to stabilize,
    # return the page height to tile in one call. See _readiness_expr.
    result = await _cdp_send(
        ws,
        msg_id_ref,
        "Runtime.evaluate",
        {
            "expression": _readiness_expr(wait_network_idle),
            "awaitPromise": True,
            "returnByValue": True,
        },
    )
    try:
        page_height = result["result"]["value"]
    except (KeyError, TypeError):
        page_height = tile_h

    tiles = []
    y = 0
    idx = 0

    while y < page_height:
        clip_h = min(tile_h, page_height - y)
        if clip_h <= 0:
            break

        # Scroll the tile into view so Chrome rasterizes it (tiles past the first
        # are otherwise blank). The top tile is already in view after load.
        if idx > 0:
            try:
                await _cdp_send(
                    ws,
                    msg_id_ref,
                    "Runtime.evaluate",
                    {"expression": _SCROLL_WAIT.format(y=y), "awaitPromise": True},
                )
            except Exception:
                pass

        params = {
            "format": image_format,
            "fromSurface": from_surface,
            "optimizeForSpeed": True,
            "clip": {
                "x": 0,
                "y": y,
                "width": viewport_w,
                "height": clip_h,
                "scale": 1,
            },
        }
        if image_format == "jpeg":
            params["quality"] = quality

        result = await _cdp_send(ws, msg_id_ref, "Page.captureScreenshot", params)

        img_bytes = base64.b64decode(result["data"])
        tile_path = (
            tile_dir / f"tile_{idx:04d}.{'jpg' if image_format == 'jpeg' else 'png'}"
        )

        if clip_h < tile_h:
            img = Image.open(io.BytesIO(img_bytes))
            w, h = img.size
            if h > clip_h:
                img = img.crop((0, 0, w, clip_h))
            img.save(
                tile_path, "JPEG" if image_format == "jpeg" else "PNG", quality=quality
            )
        else:
            tile_path.write_bytes(img_bytes)

        tiles.append(tile_path.name)
        idx += 1
        y += tile_h

    manifest = {
        "url": url,
        "page_height": page_height,
        "tiles": tiles,
        "complete": True,
    }
    with open(tile_dir / "tiles.json", "w") as f:
        json.dump(manifest, f)

    return len(tiles)
