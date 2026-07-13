def siglip_loss(query, document, logit_scale, gather_enabled=False, hardness_alpha=0.0):
    """SigLIP pairwise sigmoid loss (Zhai et al. 2023).

    Instead of softmax cross-entropy over the row, applies binary sigmoid loss
    to each (query, document) pair independently. Positive pairs should have high
    similarity, all other pairs should have low similarity.

    This avoids the softmax bottleneck where increasing one logit requires
    decreasing all others — each pair is classified independently.
    """
    if gather_enabled:
        document = gather_with_grad(document)

    device = query.device
    if query.dtype != document.dtype:
        document = document.to(query.dtype)

    num_queries = query.shape[0]
    num_docs = document.shape[0]

    # Compute scaled similarity matrix
    similarity = logit_scale(torch.matmul(query, document.T))

    # Build target matrix: +1 for positive pairs, -1 for negatives
    if gather_enabled and dist.is_initialized():
        rank = dist.get_rank()
        world_size = dist.get_world_size()
    else:
        rank = 0
        world_size = 1

    # Compute positive indices (same logic as clip_loss for hard negatives)
    labels = torch.arange(num_queries, device=device) + rank * num_queries
    assert num_docs % (num_queries * world_size) == 0
    stride = num_docs // (num_queries * world_size)
    pos_indices = labels * stride  # shape: [num_queries]

    # Target: -1 everywhere, +1 at positive positions
    target = -torch.ones(num_queries, num_docs, device=device, dtype=query.dtype)
    target.scatter_(1, pos_indices.unsqueeze(1).long(), 1.0)

    # SigLIP loss: -log_sigmoid(target * similarity) averaged over all pairs
    loss = -F.logsigmoid(target * similarity).sum() / num_queries
    if gather_enabled and dist.is_initialized():
        loss = loss * dist.get_world_size()

    # Accuracy: check if positive has highest similarity
    accuracy = (similarity.argmax(dim=1) == pos_indices).float().mean()
    return loss, accuracy
