def _capture_with_scroll(driver, output_path, scroll_pause=0.8, max_scrolls=100):
    """Capture full page by scrolling and stitching screenshots.

    Works for PDF viewers, infinite scroll pages, and other dynamic content.
    Uses image comparison to detect when scrolling has stopped.
    """
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    import tempfile
    import hashlib

    def get_screenshot_hash(path):
        """Get hash of screenshot to detect changes."""
        with Image.open(path) as img:
            return hashlib.md5(img.tobytes()).hexdigest()

    viewport_height = driver.execute_script("return window.innerHeight")
    viewport_width = driver.execute_script("return window.innerWidth")

    # Try to scroll to top using multiple methods
    driver.execute_script("window.scrollTo(0, 0)")
    actions = ActionChains(driver)
    actions.send_keys(Keys.HOME)
    actions.perform()
    time.sleep(scroll_pause)

    screenshots = []
    last_hash = None
    scroll_count = 0
    consecutive_same = 0

    while scroll_count < max_scrolls:
        # Take screenshot
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        driver.save_screenshot(temp_file.name)

        # Check if image changed (detect end of scrolling)
        current_hash = get_screenshot_hash(temp_file.name)

        if current_hash == last_hash:
            consecutive_same += 1
            os.unlink(temp_file.name)
            if consecutive_same >= 2:
                # Scrolling stopped, we've reached the end
                break
        else:
            consecutive_same = 0
            screenshots.append(temp_file.name)
            last_hash = current_hash

        # Scroll down using CDP mouse wheel event (works for PDF viewers)
        center_x = viewport_width // 2
        center_y = viewport_height // 2
        try:
            driver.execute_cdp_cmd(
                "Input.dispatchMouseEvent",
                {
                    "type": "mouseWheel",
                    "x": center_x,
                    "y": center_y,
                    "deltaX": 0,
                    "deltaY": int(viewport_height * 0.8),  # Scroll 80% of viewport
                },
            )
        except Exception:
            # Fallback to ActionChains
            actions = ActionChains(driver)
            actions.send_keys(Keys.PAGE_DOWN)
            actions.perform()

        time.sleep(scroll_pause)
        scroll_count += 1

    if not screenshots:
        driver.save_screenshot(output_path)
        return

    if len(screenshots) == 1:
        # Only one screenshot, just use it
        os.rename(screenshots[0], output_path)
        return

    # Stitch screenshots vertically
    # Each screenshot is viewport_height, but they overlap
    # We'll stack them with some overlap detection
    images = [Image.open(p) for p in screenshots]

    # Simple stacking: assume each Page Down scrolls ~80% of viewport
    overlap = int(viewport_height * 0.2)
    total_height = viewport_height + (len(images) - 1) * (viewport_height - overlap)

    stitched = Image.new("RGB", (viewport_width, total_height), (255, 255, 255))

    y_offset = 0
    for i, img in enumerate(images):
        if i == 0:
            stitched.paste(img, (0, 0))
            y_offset = viewport_height - overlap
        else:
            # Crop top overlap region and paste
            cropped = img.crop((0, overlap, viewport_width, viewport_height))
            stitched.paste(cropped, (0, y_offset))
            y_offset += viewport_height - overlap

    # Close images and clean up
    for img in images:
        img.close()
    for p in screenshots:
        if os.path.exists(p):
            os.unlink(p)

    # Trim any white space at bottom
    stitched = stitched.crop((0, 0, viewport_width, y_offset + overlap))
    stitched.save(output_path)
