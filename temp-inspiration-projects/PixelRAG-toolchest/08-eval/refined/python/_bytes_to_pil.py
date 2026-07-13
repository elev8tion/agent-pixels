def _bytes_to_pil(raw_bytes) -> Optional[Image.Image]:
    """Convert raw bytes, base64 string, dict with 'bytes' key, or PIL Image to a PIL Image.
    Returns None on failure."""
    try:
        if isinstance(raw_bytes, dict) and "bytes" in raw_bytes:
            raw_bytes = raw_bytes["bytes"]
        if isinstance(raw_bytes, list):
            raw_bytes = bytes(raw_bytes)
        if isinstance(raw_bytes, str):
            # Try base64 decoding
            try:
                decoded = base64.b64decode(raw_bytes)
                return Image.open(io.BytesIO(decoded)).convert("RGB")
            except Exception:
                pass
            return None
        if isinstance(raw_bytes, (bytes, bytearray)):
            return Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        # Already a PIL Image (HuggingFace datasets sometimes auto-decode)
        if isinstance(raw_bytes, Image.Image):
            return raw_bytes.convert("RGB")
    except Exception as e:
        logger.debug(f"Failed to convert bytes to PIL Image: {e}")
    return None
