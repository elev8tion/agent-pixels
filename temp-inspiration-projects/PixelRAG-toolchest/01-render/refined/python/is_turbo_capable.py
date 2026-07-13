def is_turbo_capable(chrome_path: str) -> bool:
    """Whether ``chrome_path`` is the pixelrag-installed patched headless_shell,
    which supports the turbo capture extensions (rawFilePath/directClip/skipRedraw).

    Deterministic by provenance — the patched binary lives only at the install path
    (with its version.json marker). No runtime probe, so a stock Chrome is never
    mistaken for a turbo-capable one (and a turbo run is never tried on a binary
    that would hang on the unknown CDP params).
    """
    try:
        installed = (INSTALL_DIR / "headless_shell").resolve()
        return (
            Path(chrome_path).resolve() == installed
            and (INSTALL_DIR / VERSION_FILE).exists()
        )
    except Exception:
        return False
