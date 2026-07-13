def get_installed_version() -> str | None:
    """Return version string of installed headless_shell, or None."""
    version_path = INSTALL_DIR / VERSION_FILE
    if version_path.exists():
        try:
            data = json.loads(version_path.read_text())
            return data.get("version")
        except Exception:
            pass
    return None
