def _save_task_query_image(
    example: dict, task_name: str, base_dir: str = "tiles"
) -> str | None:
    """Save query image from any task to disk. Returns path or None.
    Images saved to {base_dir}/{task_name}_images/{example_id}.png
    Works with PIL images, base64 strings, or dict with 'bytes' key.
    """
    img = example.get("image")
    if img is None:
        return None
    example_id = example.get("id", "unknown")
    save_dir = os.path.join(base_dir, f"{task_name}_images")
    os.makedirs(save_dir, exist_ok=True)
    out_path = os.path.join(save_dir, f"{example_id}.png")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        return out_path
    try:
        if hasattr(img, "save"):
            img.save(out_path, format="PNG")
            return out_path
        if isinstance(img, str):
            raw = (
                img.split(",", 1)[1] if img.startswith("data:") and "," in img else img
            )
            data = base64.b64decode(raw)
            with open(out_path, "wb") as f:
                f.write(data)
            return out_path
        if isinstance(img, dict) and "bytes" in img:
            b = img["bytes"]
            if b:
                with open(out_path, "wb") as f:
                    f.write(b)
                return out_path
    except Exception as e:
        logger.warning(f"Failed to save {task_name} image for {example_id}: {e}")
    return None
