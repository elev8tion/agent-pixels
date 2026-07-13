def save_checkpoint(output_dir: str, article_ids: set[int]) -> None:
    """Save embedded article IDs to checkpoint.json."""
    ckpt_path = os.path.join(output_dir, "checkpoint.json")
    data = {"embedded_article_ids": sorted(article_ids)}
    Path(ckpt_path).write_text(json.dumps(data))
    logger.info("Checkpoint saved: %d article IDs -> %s", len(article_ids), ckpt_path)
