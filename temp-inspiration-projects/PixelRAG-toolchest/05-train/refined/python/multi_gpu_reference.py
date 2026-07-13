def multi_gpu_reference(model, q_chunks, d_chunks, logit_scale):
    """Full-memory reference: forward all chunks with grad, gather, loss, backward.

    Uses the same distributed primitives (gather_with_grad, clip_loss with
    gather_enabled=True) as grad_cache_loss, but keeps all activations in
    memory for a single backward pass.
    """
    q_embs = []
    with torch.autocast("cuda", dtype=torch.bfloat16):
        for chunk in q_chunks:
            _clear_rope_deltas(model)
            q_embs.append(model(**chunk))
    q_emb = torch.cat(q_embs, dim=0)

    d_embs = []
    with torch.autocast("cuda", dtype=torch.bfloat16):
        for chunk in d_chunks:
            _clear_rope_deltas(model)
            d_embs.append(model(**chunk))
    d_emb = torch.cat(d_embs, dim=0)

    # Same loss as grad_cache_loss: gather docs across ranks, scale by world_size
    with torch.autocast("cuda", dtype=torch.bfloat16):
        loss, acc = clip_loss(q_emb, d_emb, logit_scale, gather_enabled=True)

    loss.backward()

    # Manual all_reduce to match grad_cache_loss behavior
    # (reference doesn't use DDP, so no automatic sync)
    for param in model.parameters():
        if param.requires_grad and param.grad is not None:
            dist.all_reduce(param.grad, op=dist.ReduceOp.AVG)
    for param in logit_scale.parameters():
        if param.grad is not None:
            dist.all_reduce(param.grad, op=dist.ReduceOp.AVG)

    return loss.detach(), acc.detach()
