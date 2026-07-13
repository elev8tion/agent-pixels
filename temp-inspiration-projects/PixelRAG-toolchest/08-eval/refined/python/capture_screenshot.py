def capture_screenshot(url, output_path, full_page=False, scroll_capture=False):
    """Capture screenshot of a URL.

    Args:
        url: URL to capture
        output_path: Path to save screenshot
        full_page: If True, resize window to capture full page (works for normal pages)
        scroll_capture: If True, scroll and stitch screenshots (works for PDF viewers, etc.)
    """
    driver = None
    try:
        driver = setup_driver()
        driver.get(url)
        time.sleep(3)  # Wait for initial load

        # Force lazy images to load eagerly
        _eager_load_images(driver)
        _wait_for_images(driver, timeout=5)

        if scroll_capture:
            # Scroll-based capture for PDF viewers and similar
            # just for PDF
            _capture_with_scroll(driver, output_path)
        elif full_page:
            # Get page height, keep original window width to avoid horizontal tiling
            total_height = driver.execute_script("return document.body.scrollHeight")
            current_window = driver.get_window_size()

            # Scroll through page to trigger lazy-loaded images
            _scroll_to_trigger_lazy_load(driver, total_height)

            # Re-measure height (may change after lazy content loads)
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.set_window_size(current_window["width"], total_height)
            time.sleep(0.5)

            # Final wait for any images triggered by resize
            _eager_load_images(driver)
            _wait_for_images(driver, timeout=5)

            driver.save_screenshot(output_path)
        else:
            driver.save_screenshot(output_path)

        # Convert to RGB (remove alpha channel if present)
        with Image.open(output_path) as img:
            if img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info
            ):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[3])
                img = bg
                img.save(output_path)
            elif img.mode != "RGB":
                img = img.convert("RGB")
                img.save(output_path)

        return True
    except Exception as e:
        print(f"Screenshot failed for {url}: {e}")
        return False
    finally:
        if driver:
            driver.quit()
