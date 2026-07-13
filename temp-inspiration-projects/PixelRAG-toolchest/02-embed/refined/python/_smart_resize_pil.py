def _smart_resize_pil(img: "Image.Image", max_pixels: int) -> "Image.Image":
    """Resize image to fit within max_pixels, preserving aspect ratio.

    Dimensions are rounded to multiples of 28 (Qwen3-VL patch alignment).
    """
    w, h = img.size
    if w * h <= max_pixels:
        return img
    scale = (max_pixels / (w * h)) ** 0.5
    new_w = max(round(w * scale / _RESIZE_FACTOR) * _RESIZE_FACTOR, _RESIZE_FACTOR)
    new_h = max(round(h * scale / _RESIZE_FACTOR) * _RESIZE_FACTOR, _RESIZE_FACTOR)
    return img.resize((new_w, new_h), Image.LANCZOS)
