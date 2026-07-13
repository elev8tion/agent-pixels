def preflight_simpleqa_client(vllm_url="", model_name=""):
    """Check SimpleQA answer/judge client before expensive model loading."""
    try:
        client = build_openai_client(vllm_url, timeout=30)
        client.models.list()
        target = vllm_url or "openai"
        logger.info(f"SimpleQA API preflight OK: target={target} model={model_name}")
        return True
    except Exception as e:
        target = vllm_url or "openai"
        logger.warning(f"SimpleQA API preflight failed for {target}: {e}")
        return False
