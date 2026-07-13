def chunked_reference_forward_backward(model, q_chunks, d_chunks, logit_scale):
    """Full-memory reference: forward ALL chunks with grad, then single backward.

    This computes the EXACT SAME embeddings as GradCache step 1 (same chunks,
    same order, same autocast), but keeps all activations for a single backward.
    """
    # Forward each chunk with grad, same as GradCache would
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

    # Same loss computation as GradCache step 2
    # gather_enabled=True with no dist → effectively gather_enabled=False
    with torch.autocast("cuda", dtype=torch.bfloat16):
        loss, acc = clip_loss(q_emb, d_emb, logit_scale, gather_enabled=True)

    loss.backward()
    return loss.detach(), acc.detach()
