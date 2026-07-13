def setup_driver(window_width=1024, window_height=2000, device_scale_factor=1):
    """Set up Chrome WebDriver.

    Args:
        window_width: Viewport width (1024 = tile width, ensures screenshots align with tile grid).
        window_height: Initial viewport height.
        device_scale_factor: Pixel density (1 = standard, 2 = retina quality).
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    import shutil

    snap_chromedriver = "/snap/bin/chromium.chromedriver"
    if os.path.exists(snap_chromedriver):
        driver_path = snap_chromedriver
    elif shutil.which("chromedriver"):
        driver_path = shutil.which("chromedriver")
    else:
        driver_path = ChromeDriverManager().install()
    service = Service(driver_path)
    options = webdriver.ChromeOptions()

    # Find Chrome binary path
    chrome_binary = None
    for chrome_path in [
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
    ]:
        if os.path.exists(chrome_path):
            chrome_binary = chrome_path
            break

    if chrome_binary:
        options.binary_location = chrome_binary

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--window-size={window_width},{window_height}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--no-zygote")
    options.add_argument("--remote-debugging-port=0")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    )
    # Retina-quality rendering (2x pixel density)
    if device_scale_factor and device_scale_factor > 1:
        options.add_argument(f"--force-device-scale-factor={device_scale_factor}")
    driver = webdriver.Chrome(service=service, options=options)
    return driver
