def encode_image_for_vlm(image_path, max_pixels: int = 89_000_000):
    """Encode image to base64 for VLM ground truth, minimal processing.

    For Ground Truth evaluation, we want to preserve original image quality
    and let the VLM handle resizing according to its own requirements.
    Only applies PIL safety limit (89M pixels).

    Args:
        image_path: Path to image file.
        max_pixels: Maximum pixels (default 89M, PIL's safety limit).
    """
    if not os.path.exists(image_path):
        return None

    try:
        # Increase PIL limit temporarily
        Image.MAX_IMAGE_PIXELS = 300_000_000

        with Image.open(image_path) as img:
            total_pixels = img.width * img.height

            # Only compress if exceeds PIL safety limit
            if total_pixels <= max_pixels:
                # Just read and encode directly - no resize
                with open(image_path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")

            # Compress only if exceeds max_pixels
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Scale down to fit max_pixels
            ratio = (max_pixels / total_pixels) ** 0.5
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Encode to JPEG
            from io import BytesIO

            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            return base64.b64encode(buffered.getvalue()).decode("utf-8")

    except Exception as e:
        print(f"Failed to encode image {image_path}: {e}")
        return None
