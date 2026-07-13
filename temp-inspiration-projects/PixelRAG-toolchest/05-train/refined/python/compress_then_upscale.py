def compress_then_upscale(src: str, dst: str, scale_factor: float) -> bool:
    """Downscale by scale_factor/dim, then upscale back to original size."""
    try:
        Image.MAX_IMAGE_PIXELS = 300_000_000
        with Image.open(src) as img:
            orig_w, orig_h = img.width, img.height
            new_w = max(1, int(orig_w * scale_factor))
            new_h = max(1, int(orig_h * scale_factor))
            if img.mode != "RGB":
                img = img.convert("RGB")
            small = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            # Upscale back to original
            upscaled = small.resize((orig_w, orig_h), Image.Resampling.LANCZOS)
            upscaled.save(dst, format="PNG")
        return True
    except Exception as e:
        print(f"  WARN: compress+upscale failed {src}: {e}", file=sys.stderr)
        return False
