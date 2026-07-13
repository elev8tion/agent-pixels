def install_chrome(version: str | None = None, force: bool = False) -> Path:
    """Download and install the patched headless_shell binary.

    Args:
        version: Chrome version to install. Defaults to CHROME_VERSION.
        force: Re-download even if already installed.

    Returns:
        Path to the installed headless_shell binary.
    """
    version = version or CHROME_VERSION
    binary_path = INSTALL_DIR / "headless_shell"

    if binary_path.exists() and not force:
        installed = get_installed_version()
        if installed == version:
            print(f"Already installed: headless_shell {version}")
            return binary_path

    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise RuntimeError(
            f"Pre-built headless_shell only available for linux-x64, "
            f"got {platform.system()}-{platform.machine()}"
        )

    url = RELEASE_URL_TEMPLATE.format(version=version)
    print(f"Downloading headless_shell {version}...")
    print(f"  URL: {url}")

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".tar.zst", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        urllib.request.urlretrieve(url, tmp_path, _progress_hook)
        print()

        # Decompress: zstd → tar → extract
        print("Extracting...")
        # Try zstd decompression
        decomp_path = tmp_path + ".tar"
        try:
            subprocess.run(
                ["zstd", "-d", tmp_path, "-o", decomp_path],
                check=True,
                capture_output=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            # Fallback: try python zstandard
            try:
                import zstandard

                with open(tmp_path, "rb") as f_in, open(decomp_path, "wb") as f_out:
                    dctx = zstandard.ZstdDecompressor()
                    dctx.copy_stream(f_in, f_out)
            except ImportError:
                raise RuntimeError(
                    "zstd not found. Install with: apt install zstd (or pip install zstandard)"
                )

        with tarfile.open(decomp_path) as tar:
            tar.extractall(INSTALL_DIR)
        os.unlink(decomp_path)

        # Set executable permission
        binary_path.chmod(0o755)

        # Write version file
        version_data = {"version": version, "binary": str(binary_path)}
        (INSTALL_DIR / VERSION_FILE).write_text(json.dumps(version_data))

        print(
            f"Installed: {binary_path} ({binary_path.stat().st_size / 1024 / 1024:.0f}MB)"
        )
        return binary_path

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
