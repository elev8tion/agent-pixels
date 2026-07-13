def render_pdf(
    path: str | Path,
    output_dir: str | Path,
    *,
    dpi: int = 200,
    pages: Optional[list[int]] = None,
    quality: int = 85,
) -> list[Path]:
    """Render a PDF file to tiled JPEG images.

    Args:
        path: Path to the PDF file.
        output_dir: Directory to write the tile subdirectory into.
        dpi: Rendering resolution (default 200 ≈ 1650×2200 for A4).
        pages: 1-based list of page numbers to render. ``None`` renders all.
        quality: JPEG quality 1-100 (default 85).

    Returns:
        List containing the tile directory Path on success.
    """
    from .backends.pdf import render_pdf as _render_pdf

    return _render_pdf(path, output_dir, dpi=dpi, pages=pages, quality=quality)
