def compress_image(src: str, dst: str, scale_factor: float) -> bool:
    try:
        Image.MAX_IMAGE_PIXELS = 300_000_000
        with Image.open(src) as img:
            new_w = max(1, int(img.width * scale_factor))
            new_h = max(1, int(img.height * scale_factor))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            img_resized.save(dst, format="PNG")
        return True
    except Exception as e:
        print(f"  WARN: compress failed {src}: {e}", file=sys.stderr)
        return False
