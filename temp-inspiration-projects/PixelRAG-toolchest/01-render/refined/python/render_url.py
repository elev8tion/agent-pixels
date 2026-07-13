def render_url(
    url: str,
    output_dir: str | Path,
    backend: str = "cdp",
    *,
    tile_height: int = 8192,
    quality: int = 85,
    viewport_width: int = 875,
    workers: int = 1,
    **kwargs,
) -> list[Path]:
    """Render a URL to tiled JPEG images.

    Args:
        url: URL to capture (http:// or https:// or file://).
        output_dir: Directory to write tile subdirectories into.
        backend: Rendering backend: ``"cdp"`` (default, fastest) or
                 ``"playwright"`` (full-featured).
        tile_height: Maximum tile height in pixels (default 8192).
        quality: JPEG quality 1-100 (default 85).
        viewport_width: Browser viewport width in pixels (default 875).
        workers: Number of parallel browser processes (default 1).
        **kwargs: Additional keyword arguments forwarded to the backend.

    Returns:
        List of Path objects pointing to created tile directories.
    """
    return render_urls(
        [url],
        output_dir,
        backend=backend,
        tile_height=tile_height,
        quality=quality,
        viewport_width=viewport_width,
        workers=workers,
        **kwargs,
    )
