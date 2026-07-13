def clip_loss(
    query,
    document,
    logit_scale,
    gather_enabled=False,
    hardness_alpha=0.0,
    label_smoothing=0.0,
):
    """InfoNCE contrastive loss with hard negative support (from contrastors/loss.py).

    Inspired by: https://github.com/mlfoundations/open_clip/blob/main/src/open_clip/loss.py#L66

    When hard negatives are used, document contains interleaved positives and negatives:
        [pos1, neg1a, neg1b, pos2, neg2a, neg2b, ...]
    So document.size(0) = query.size(0) * (1 + num_hard_negatives).
    Labels point to the positive positions: [0, 3, 6, 9, ...] for 2 hard negs.

    hardness_alpha: LLaVE-style hardness weighting (Lan et al. 2025). When > 0,
    adds alpha * cos_sim(q, d) to negative logits before softmax, so harder
    negatives get upweighted. 0 = off (standard InfoNCE).
    """
    if gather_enabled:
        document = gather_with_grad(document)

    device = query.device

    if query.dtype != document.dtype:
        document = document.to(query.dtype)

    num_queries = query.shape[0]
    labels = torch.arange(num_queries).to(device)

    similarity = logit_scale(torch.matmul(query, document.T))

    # Rank offset and world_size scaling only apply when documents are gathered
    # across ranks. Without gather, each rank evaluates independently (local labels).
    if gather_enabled and dist.is_initialized():
        rank = dist.get_rank()
        world_size = dist.get_world_size()
    else:
        rank = 0
        world_size = 1

    labels = labels + rank * num_queries
    # Scale for hard negatives: docs_per_query_per_rank = doc.size(0) / (N * W)
    assert document.size(0) % (num_queries * world_size) == 0, (
        f"document.size(0)={document.size(0)} not divisible by "
        f"num_queries*world_size={num_queries}*{world_size}"
    )
    labels = labels * (document.size(0) // (num_queries * world_size))

    # LLaVE hardness weighting: upweight harder negatives in softmax
    if hardness_alpha > 0:
        with torch.no_grad():
            raw_sim = torch.matmul(query, document.T)
        neg_mask = torch.ones_like(similarity, dtype=torch.bool)
        neg_mask.scatter_(1, labels.unsqueeze(1), False)
        similarity = similarity + hardness_alpha * raw_sim * neg_mask

    loss = F.cross_entropy(similarity, labels, label_smoothing=label_smoothing)
    if gather_enabled and dist.is_initialized():
        loss = loss * dist.get_world_size()

    # accuracy for logging
    accuracy = (similarity.argmax(dim=1) == labels).float().mean()
    return loss, accuracy
