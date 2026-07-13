def _clamp_width_pil(
    img: "Image.Image", max_width: int = _MAX_CHUNK_WIDTH
) -> "Image.Image":
    """Resize image so width <= max_width, preserving aspect ratio.

    Dimensions are rounded to multiples of 28 (Qwen3-VL patch alignment).
    Used for PDF tiles that render wider than the web viewport.
    """
    w, h = img.size
    if w <= max_width:
        return img
    scale = max_width / w
    new_w = max(round(w * scale / _RESIZE_FACTOR) * _RESIZE_FACTOR, _RESIZE_FACTOR)
    new_h = max(round(h * scale / _RESIZE_FACTOR) * _RESIZE_FACTOR, _RESIZE_FACTOR)
    return img.resize((new_w, new_h), Image.LANCZOS)
