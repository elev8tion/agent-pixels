def encode_image_base64(path: str) -> str:
    """Read and base64-encode an image. Returns the raw base64 string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")
