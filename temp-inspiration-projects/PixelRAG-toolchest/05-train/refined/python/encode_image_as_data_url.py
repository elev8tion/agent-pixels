def encode_image_as_data_url(path: str) -> str:
    ext = Path(path).suffix.lower().lstrip(".") or "png"
    mime = "image/png" if ext == "png" else f"image/{ext}"
    try:
        raw = Path(path).read_bytes()
    except FileNotFoundError as exc:
        raise MissingImageError(path) from exc
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"
