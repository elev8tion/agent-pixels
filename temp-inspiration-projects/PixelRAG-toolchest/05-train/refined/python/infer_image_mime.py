def infer_image_mime(path: str) -> str:
    ext = Path(path).suffix.lower().lstrip(".") or "png"
    return "image/png" if ext == "png" else f"image/{ext}"
