def load_checkpoint(output_dir: str) -> set[int]:
    """Load set of already-embedded article IDs from checkpoint.json."""
    ckpt_path = os.path.join(output_dir, "checkpoint.json")
    if not os.path.exists(ckpt_path):
        return set()
    try:
        data = json.loads(Path(ckpt_path).read_text())
        return set(data.get("embedded_article_ids", []))
    except Exception as e:
        logger.warning("Failed to load checkpoint %s: %s", ckpt_path, e)
        return set()
