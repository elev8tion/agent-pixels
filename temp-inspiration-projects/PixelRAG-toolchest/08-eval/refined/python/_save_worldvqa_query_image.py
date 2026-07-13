def _save_worldvqa_query_image(example: dict, base_dir: str = "tiles") -> str | None:
    """Save WorldVQA query image to disk. Returns path or None.
    Images saved to {base_dir}/worldvqa_images/{example_id}.png
    """
    img = example.get("image")
    if img is None:
        return None
    example_id = example.get("id", "unknown")
    save_dir = os.path.join(base_dir, "worldvqa_images")
    os.makedirs(save_dir, exist_ok=True)
    out_path = os.path.join(save_dir, f"{example_id}.png")

    try:
        if hasattr(img, "save"):
            img.save(out_path, format="PNG")
            return out_path
        if isinstance(img, str):
            raw = (
                img.split(",", 1)[1] if img.startswith("data:") and "," in img else img
            )
            data = base64.b64decode(raw)
            ext = ".png" if data[:8] == b"\x89PNG\r\n\x1a\n" else ".jpg"
            out_path = os.path.join(save_dir, f"{example_id}{ext}")
            with open(out_path, "wb") as f:
                f.write(data)
            return out_path
        if isinstance(img, dict) and "bytes" in img:
            b = img["bytes"]
            if b:
                ext = ".png" if b[:8] == b"\x89PNG\r\n\x1a\n" else ".jpg"
                out_path = os.path.join(save_dir, f"{example_id}{ext}")
                with open(out_path, "wb") as f:
                    f.write(b)
                return out_path
    except Exception as e:
        logger.warning(f"Failed to save WorldVQA image for {example_id}: {e}")
    return None
