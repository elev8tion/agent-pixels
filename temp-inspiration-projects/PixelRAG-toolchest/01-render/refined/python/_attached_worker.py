async def _attached_worker(
    http_base: str,
    browser_ws_url: str,
    cdp_url: str,
    work_queue: asyncio.Queue,
    output_dir: Path,
    tile_height: int,
    quality: int,
    viewport_w: int,
    image_format: str,
    from_surface: bool,
    wait_network_idle: bool,
    worker_id: int,
    stats: dict,
    results: list,
):
    """Async worker that attaches to an already-running browser over CDP.

    Mirrors ``_worker`` but, instead of launching a throwaway ``--headless``
    process, creates its own fresh tab (target) in the existing browser, drives
    only that tab, and closes only that tab on teardown. The browser's profile
    — cookies, logins — is whatever the running instance has, so authenticated
    pages render. Never touches the user's other tabs; never kills the browser.
    """
    browser_ws = await _connect_ws(browser_ws_url)
    bmsg = [0]
    target_id = None
    try:
        created = await _cdp_send(
            browser_ws, bmsg, "Target.createTarget", {"url": "about:blank"}
        )
        target_id = created["targetId"]
        ws = await _connect_ws(
            await _page_ws_url_for_target(http_base, target_id, cdp_url)
        )
        msg_id_ref = [0]

        await _setup_page(ws, msg_id_ref, viewport_w, tile_height, wait_network_idle)
        await _drain_queue(
            ws,
            msg_id_ref,
            work_queue,
            output_dir,
            tile_height,
            quality,
            viewport_w,
            image_format,
            from_surface,
            wait_network_idle,
            worker_id,
            stats,
            results,
        )
        await ws.close()
    finally:
        # Close only the tab we created; leave the browser and its other tabs alone.
        if target_id is not None:
            try:
                await _cdp_send(
                    browser_ws, bmsg, "Target.closeTarget", {"targetId": target_id}
                )
            except Exception:
                pass
        await browser_ws.close()
