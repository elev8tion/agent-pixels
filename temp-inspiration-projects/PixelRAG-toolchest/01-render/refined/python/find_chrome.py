def find_chrome(auto_install: bool = True) -> str:
    """Find the best available Chrome binary. Auto-installs on linux-x64 if none found.

    Search order (per OS): CHROME_PATH → pixelrag-installed headless_shell →
    Playwright's Chromium → system Chrome/Chromium → (linux-x64) auto-install.

    Returns:
        Path to Chrome binary.

    Raises:
        FileNotFoundError: No Chrome binary found (and auto-install unavailable).
    """
    for path in _candidate_chrome_paths():
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    # The prebuilt (turbo) headless_shell is published only for linux-x64.
    if auto_install and platform.system() == "Linux" and platform.machine() == "x86_64":
        print("No Chrome found. Installing headless_shell...", flush=True)
        return str(install_chrome())

    raise FileNotFoundError(
        "No Chrome binary found. Install Google Chrome or Chromium, or set CHROME_PATH "
        "to its executable. (The bundled headless_shell auto-installs on linux-x64 only.)"
    )
