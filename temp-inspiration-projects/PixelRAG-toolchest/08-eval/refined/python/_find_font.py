def _find_font(font_path: str | None = None) -> str:
    """Find a usable TrueType font on this system."""
    if font_path and os.path.exists(font_path):
        return font_path
    for candidate in _FONT_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "No suitable TTF font found. Install dejavu or liberation fonts, "
        "or pass font_path explicitly."
    )
