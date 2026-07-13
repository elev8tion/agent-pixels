def _worldvqa_image_to_base64(img) -> str | None:
    """Convert WorldVQA image (PIL, base64 str, or dict) to base64 string."""
    if img is None:
        return None
    if isinstance(img, str):
        if img.startswith("data:"):
            if "," in img:
                return img.split(",", 1)[1]
        return img
    if hasattr(img, "save"):
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    if isinstance(img, dict) and "bytes" in img:
        b = img["bytes"]
        return base64.b64encode(b).decode() if b else None
    return None
