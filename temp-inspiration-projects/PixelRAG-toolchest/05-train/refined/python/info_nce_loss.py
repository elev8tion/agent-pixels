def info_nce_loss(
    q_emb: torch.Tensor, i_emb: torch.Tensor, temperature: float = 0.07
) -> torch.Tensor:
    """In-batch negatives InfoNCE loss.

    q_emb: (B, D) L2-normalized query embeddings
    i_emb: (B, D) L2-normalized image embeddings
    Diagonal entries are positive pairs.
    """
    logits = q_emb @ i_emb.T / temperature  # (B, B)
    labels = torch.arange(logits.size(0), device=logits.device)
    return F.cross_entropy(logits, labels)
