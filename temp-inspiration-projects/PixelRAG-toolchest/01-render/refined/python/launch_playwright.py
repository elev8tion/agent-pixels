async def launch_playwright(chrome_path: str) -> PlaywrightConnection:
    """Launch Chrome via Playwright, get CDP session."""
    from playwright.async_api import async_playwright

    pw = await async_playwright().start()
    browser = await pw.chromium.launch(
        headless=True, executable_path=chrome_path, args=CHROME_ARGS
    )
    ctx = await browser.new_context(
        viewport={"width": 875, "height": 8192},
        device_scale_factor=1,
    )
    page = await ctx.new_page()
    cdp_session = await ctx.new_cdp_session(page)
    return PlaywrightConnection(page, cdp_session, browser, pw)
