def encode_image(image_path, max_pixels: int = 150_000_000, max_height: int = 8000):
    """Encode image to base64, compressing if too large.

    Used for Vector DB retrieval where consistent image sizes help with embedding.

    Args:
        image_path: Path to image file.
        max_pixels: Maximum pixels allowed (default 150M).
        max_height: Maximum height in pixels (default 8000).
    """
    if not os.path.exists(image_path):
        return None

    try:
        # Increase PIL limit temporarily
        Image.MAX_IMAGE_PIXELS = 300_000_000

        with Image.open(image_path) as img:
            # Check if compression needed
            total_pixels = img.width * img.height
            needs_compression = total_pixels > max_pixels or img.height > max_height

            if not needs_compression:
                # Just read and encode directly
                with open(image_path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")

            # Compress: resize to fit within limits
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Calculate new size
            if img.height > max_height:
                ratio = max_height / img.height
                new_width = int(img.width * ratio)
                new_height = max_height
            else:
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
