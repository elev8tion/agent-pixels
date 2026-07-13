def pool_and_normalize(hidden_states, attention_mask):
    """Last-token pooling + L2 normalization.

    Matches the production embedding pipeline (embed_tiles.py direct_gpu backend).
    """
    last_idx = attention_mask.sum(dim=1) - 1
    pooled = hidden_states[
        torch.arange(hidden_states.size(0), device=hidden_states.device),
        last_idx,
    ]
    return F.normalize(pooled, p=2, dim=-1)
