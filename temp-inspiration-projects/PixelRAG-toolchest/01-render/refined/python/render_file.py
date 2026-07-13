def render_file(
    path: str | Path,
    output_dir: str | Path,
    backend: str = "cdp",
    **kwargs,
) -> list[Path]:
    """Auto-detect file type and render to tiled JPEG images.

    Dispatch rules:
    - ``.pdf`` → ``render_pdf()``
    - ``.html`` / ``.htm`` → ``render_url(file://...)``
    - ``.png`` / ``.jpg`` / ``.jpeg`` / ``.webp`` → copy into output_dir as-is
    - ``http://`` or ``https://`` prefix → ``render_url()``

    Args:
        path: Path to a local file, or a URL string.
        output_dir: Directory to write tile subdirectories into.
        backend: Browser backend for HTML/URL rendering (default ``"cdp"``).
        **kwargs: Forwarded to the underlying render function.

    Returns:
        List of Path objects pointing to created tile directories or copied files.
    """
    path_str = str(path)
    output_dir = Path(output_dir)

    # URL strings
    if path_str.startswith("http://") or path_str.startswith("https://"):
        return render_url(path_str, output_dir, backend=backend, **kwargs)

    p = Path(path)
    suffix = p.suffix.lower()

    if suffix == ".pdf":
        return render_pdf(p, output_dir, **kwargs)

    if suffix in {".html", ".htm"}:
        file_url = p.resolve().as_uri()
        return render_url(file_url, output_dir, backend=backend, **kwargs)

    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        output_dir.mkdir(parents=True, exist_ok=True)
        dest = output_dir / p.name
        shutil.copy2(str(p), str(dest))
        logger.info("Copied image: %s → %s", p, dest)
        return [dest]

    raise ValueError(
        f"Cannot auto-detect render method for {path!r}. "
        "Supported: .pdf, .html, .htm, .png, .jpg, .jpeg, .webp, http://, https://"
    )
