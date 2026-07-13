def _scroll_to_trigger_lazy_load(driver, page_height):
    """Scroll through the page to trigger lazy-loaded content, then scroll back to top."""
    viewport_height = driver.execute_script("return window.innerHeight") or 1080
    y = 0
    while y < page_height:
        driver.execute_script(f"window.scrollTo(0, {y})")
        time.sleep(0.15)
        _eager_load_images(driver)
        y += viewport_height
    # Wait for all images to load after full scroll
    _wait_for_images(driver, timeout=10)
    # Scroll back to top
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(0.3)
