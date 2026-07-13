async def _setup_page(
    ws, msg_id_ref: list, viewport_w: int, tile_height: int, wait_network_idle: bool
):
    """Enable the CDP domains and fix the viewport for a page ws before capture."""
    await _cdp_send(ws, msg_id_ref, "Page.enable")
    if wait_network_idle:
        # PerformanceObserver (used by the idle wait) needs no CDP domain, but
        # enabling Network keeps resource timing reliable across navigations.
        await _cdp_send(ws, msg_id_ref, "Network.enable")
    await _cdp_send(
        ws,
        msg_id_ref,
        "Emulation.setDeviceMetricsOverride",
        {
            "width": viewport_w,
            "height": tile_height,
            "deviceScaleFactor": 1,
            "mobile": False,
        },
    )
