def encode_image(path: str, max_bytes: int = 4_000_000) -> str | None:
    """Return base64 data-URL for the image; return None if missing/too-big."""
    try:
        with open(path, "rb") as f:
            data = f.read()
        if len(data) > max_bytes:
            # For large images, re-encode smaller via PIL to stay under limit
            from PIL import Image
            import io

            Image.MAX_IMAGE_PIXELS = 300_000_000
            img = Image.open(path)
            if img.mode != "RGB":
                img = img.convert("RGB")
            # Shrink longest side to 1024 if larger
            w, h = img.size
            m = max(w, h)
            if m > 1024:
                s = 1024 / m
                img = img.resize((int(w * s), int(h * s)), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            data = buf.getvalue()
        b64 = base64.b64encode(data).decode("ascii")
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        print(f"  WARN: encode {path}: {e}", file=sys.stderr)
        return None
