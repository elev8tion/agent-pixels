def _candidate_chrome_paths(system: str | None = None) -> list[str]:
    """Ordered Chrome binary candidates for the given OS (default: this OS).

    Order: CHROME_PATH env → pixelrag-installed patched headless_shell →
    Playwright's Chromium (newest version first) → system Chrome/Chromium.
    Playwright and system locations are OS-specific so the skill works on
    macOS and Windows, not only Linux.
    """
    import glob

    system = system or platform.system()
    home = Path.home()
    paths: list[str] = []

    env = os.environ.get("CHROME_PATH", "")
    if env:
        paths.append(env)
    # Bundled patched headless_shell (only installed on linux-x64, harmless elsewhere).
    paths.append(str(INSTALL_DIR / "headless_shell"))

    def add_playwright(cache_dir: Path, rel_glob: str) -> None:
        # Newest chromium-NNNN first.
        paths.extend(sorted(glob.glob(str(cache_dir / rel_glob)), reverse=True))

    if system == "Darwin":
        add_playwright(
            home / "Library" / "Caches" / "ms-playwright",
            "chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
        )
        paths += [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    elif system == "Windows":
        localappdata = os.environ.get("LOCALAPPDATA", "")
        if localappdata:
            add_playwright(
                Path(localappdata) / "ms-playwright",
                "chromium-*/chrome-win*/chrome.exe",
            )
        for base in (
            os.environ.get("PROGRAMFILES", r"C:\Program Files"),
            os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
            localappdata,
        ):
            if base:
                paths.append(str(Path(base) / "Google/Chrome/Application/chrome.exe"))
    else:  # Linux / other
        add_playwright(
            home / ".cache" / "ms-playwright", "chromium-*/chrome-linux*/chrome"
        )
        paths += [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]
    return paths
