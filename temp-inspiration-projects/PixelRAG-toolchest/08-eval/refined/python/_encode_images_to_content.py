def _encode_images_to_content(
    images: list[tuple[str, float]], encode_image_fn
) -> list[dict]:
    """Encode image paths to base64 content blocks."""
    content = []
    for img_path, score in images:
        if os.path.exists(img_path):
            try:
                img_base64 = encode_image_fn(img_path)
                if img_base64:
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_base64}"},
                        }
                    )
            except Exception as e:
                logger.warning(f"Failed to encode image {img_path}: {e}")
    return content
