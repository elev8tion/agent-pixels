def render_urls(
    urls: list[str],
    output_dir: str | Path,
    backend: str = "cdp",
    *,
    stems: list[str] | None = None,
    tile_height: int = 8192,
    quality: int = 85,
    viewport_width: int = 875,
    workers: int = 4,
    **kwargs,
) -> list[Path]:
    """Render a list of URLs to tiled JPEG images.

    Args:
        urls: URLs to capture.
        output_dir: Directory to write tile subdirectories into.
        backend: ``"cdp"`` (default) or ``"playwright"``.
        stems: Optional list of output directory stems (one per URL).
               If provided, tiles are written to ``{output_dir}/{stem}.png.tiles/``
               instead of deriving names from URLs. Useful for assigning
               sequential IDs (e.g. ``["0", "1", "2"]``).
        tile_height: Maximum tile height in pixels (default 8192).
        quality: JPEG quality 1-100 (default 85).
        viewport_width: Browser viewport width in pixels (default 875).
        workers: Number of parallel browser processes (default 4).
        **kwargs: Additional keyword arguments forwarded to the backend.

    Returns:
        List of Path objects pointing to created tile directories.
    """
    if backend in ("cdp", "websocket"):  # "websocket" kept as a back-compat alias
        from .backends.cdp import render_urls as _render_urls
    else:
        raise ValueError(
            f"Unknown backend: {backend!r}. Choose 'cdp'."
            " The cdp backend auto-selects a turbo capture path when a turbo-capable"
            " Chrome is present."
        )

    return _render_urls(
        urls,
        output_dir,
        stems=stems,
        tile_height=tile_height,
        quality=quality,
        viewport_width=viewport_width,
        workers=workers,
        **kwargs,
    )
