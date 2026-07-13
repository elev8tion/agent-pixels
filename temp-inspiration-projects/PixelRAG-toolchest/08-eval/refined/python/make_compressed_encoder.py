def make_compressed_encoder(compress_ratio: int, save_dir: str | None = None):
    """Create an image encoder that downscales images before encoding to base64.

    The compression ratio N divides the total pixel count by N, i.e. each
    dimension is scaled by 1/sqrt(N).  For a 1024x1024 tile:
      - ratio  1 ->  1024x1024  (no compression, baseline)
      - ratio  4 ->   512x512
      - ratio  9 ->  ~341x341
      - ratio 16 ->   256x256
      - ratio 25 ->  ~205x205

    Uses LANCZOS resampling (best quality for downscaling).

    Compressed images are saved to ``save_dir`` (if provided) so they can
    be visually inspected later.  The mapping from original path to saved
    compressed path is recorded in ``encoder.compressed_paths`` (a dict
    attached to the returned function object).

    Args:
        compress_ratio: Pixel compression ratio (1 = no compression).
        save_dir: Directory to save compressed images. If None, a default
                  directory ``compressed_tiles_{ratio}x`` is used.

    Returns:
        A function with the same signature as ``encode_screenshot`` that
        first downscales the image, then encodes it to base64.
        The function has an attribute ``compressed_paths: dict[str, str]``
        mapping original_path -> compressed_path.
    """
    if compress_ratio <= 1:
        # No compression – use the normal encoder
        return encode_screenshot

    import math

    scale_factor = 1.0 / math.sqrt(compress_ratio)

    # Set up save directory
    if save_dir is None:
        save_dir = f"compressed_tiles_{compress_ratio}x"
    os.makedirs(save_dir, exist_ok=True)

    logger.info(
        f"Pixel compression enabled: ratio={compress_ratio}, "
        f"scale_factor={scale_factor:.4f} per dimension, "
        f"saving compressed images to {save_dir}"
    )

    # Shared dict to track original -> compressed path mapping
    _compressed_paths: dict[str, str] = {}

    def _compressed_encode(screenshot_path: str) -> str | None:
        """Encode image with pixel compression and save to disk."""
        import base64 as _b64
        from io import BytesIO
        from PIL import Image as _Image

        if not screenshot_path or not os.path.exists(screenshot_path):
            return None

        try:
            _Image.MAX_IMAGE_PIXELS = 300_000_000
            with _Image.open(screenshot_path) as img:
                new_w = max(1, int(img.width * scale_factor))
                new_h = max(1, int(img.height * scale_factor))

                if img.mode != "RGB":
                    img = img.convert("RGB")

                img_resized = img.resize((new_w, new_h), _Image.Resampling.LANCZOS)

                # Save compressed image to disk
                basename = os.path.splitext(os.path.basename(screenshot_path))[0]
                compressed_filename = f"{basename}_compress{compress_ratio}x.png"
                compressed_path = os.path.join(save_dir, compressed_filename)
                img_resized.save(compressed_path, format="PNG")
                _compressed_paths[screenshot_path] = compressed_path

                # Encode to base64 from the saved file
                buf = BytesIO()
                img_resized.save(buf, format="PNG")
                return _b64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception as e:
            logger.error(f"Compressed encode failed for {screenshot_path}: {e}")
            return None

    # Attach the path mapping dict to the function so callers can access it
    _compressed_encode.compressed_paths = _compressed_paths
    _compressed_encode.compress_ratio = compress_ratio
    _compressed_encode.save_dir = save_dir

    return _compressed_encode
