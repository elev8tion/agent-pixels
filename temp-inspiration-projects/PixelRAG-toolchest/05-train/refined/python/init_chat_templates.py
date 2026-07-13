def init_chat_templates(processor):
    """Pre-compute chat template strings once to avoid per-batch overhead."""
    global \
        _QUERY_PREFIX, \
        _QUERY_SUFFIX, \
        _DOC_IMAGE_TMPL, \
        _DOC_TEXT_PREFIX, \
        _DOC_TEXT_SUFFIX
    # Query template with placeholder
    q_msgs = [
        {"role": "system", "content": [{"type": "text", "text": QUERY_INSTRUCTION}]},
        {"role": "user", "content": [{"type": "text", "text": "PLACEHOLDER"}]},
    ]
    q_text = processor.apply_chat_template(
        q_msgs, tokenize=False, add_generation_prompt=True
    )
    idx = q_text.index("PLACEHOLDER")
    _QUERY_PREFIX = q_text[:idx]
    _QUERY_SUFFIX = q_text[idx + len("PLACEHOLDER") :]
    # Image doc template is fully static (no per-sample text)
    d_msgs = [
        {"role": "system", "content": [{"type": "text", "text": DOC_INSTRUCTION}]},
        {"role": "user", "content": [{"type": "image"}]},
    ]
    _DOC_IMAGE_TMPL = processor.apply_chat_template(
        d_msgs, tokenize=False, add_generation_prompt=True
    )
    # Text doc template with placeholder (for text-only training)
    dt_msgs = [
        {"role": "system", "content": [{"type": "text", "text": DOC_INSTRUCTION}]},
        {"role": "user", "content": [{"type": "text", "text": "PLACEHOLDER"}]},
    ]
    dt_text = processor.apply_chat_template(
        dt_msgs, tokenize=False, add_generation_prompt=True
    )
    dt_idx = dt_text.index("PLACEHOLDER")
    _DOC_TEXT_PREFIX = dt_text[:dt_idx]
    _DOC_TEXT_SUFFIX = dt_text[dt_idx + len("PLACEHOLDER") :]
    logger.info(f"Query prefix: {repr(_QUERY_PREFIX)}")
    logger.info(f"Doc image template: {repr(_DOC_IMAGE_TMPL[:80])}...")
    logger.info(f"Doc text prefix: {repr(_DOC_TEXT_PREFIX)}")
