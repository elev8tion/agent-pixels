def _wait_for_images(driver, timeout=10):
    """Wait for all document images to finish loading (load or error)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        pending = driver.execute_script("""
            return Array.from(document.images || [])
                .filter(function(img) { return !(img.complete && img.naturalWidth > 0); }).length;
        """)
        if pending == 0:
            return
        time.sleep(0.3)
