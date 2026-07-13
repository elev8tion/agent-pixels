def encode_image_base64(path: str) -> str:
    try:
        raw = Path(path).read_bytes()
    except FileNotFoundError as exc:
        raise MissingImageError(path) from exc
    return base64.b64encode(raw).decode("ascii")
