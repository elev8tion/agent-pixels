def _remap_keys(state_dict):
    """Remap checkpoint keys from ConditionalGeneration to bare Model format."""
    new_sd = {}
    for key, value in state_dict.items():
        new_key = key
        for pattern, replacement in _KEY_MAPPINGS:
            if pattern.search(new_key):
                new_key = pattern.sub(replacement, new_key)
                break
        # Skip lm_head and other keys not in Qwen3VLModel
        if new_key.startswith("lm_head"):
            continue
        new_sd[new_key] = value
    return new_sd
