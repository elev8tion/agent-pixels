def direct_loss_query_side(
    query_model,
    frozen_doc_model,
    q_inputs,
    d_inputs,
    logit_scale,
    gather_enabled=True,
    debug_enabled=False,
    hardness_alpha=0.0,
):
    """Simpler query-side training path without GradCache."""
    raw_query_model = (
        query_model.module if hasattr(query_model, "module") else query_model
    )
    debug_trace(debug_enabled, "direct_query_side: query forward")
    with torch.autocast("cuda", dtype=torch.bfloat16):
        _clear_rope_deltas(raw_query_model)
        q_emb = raw_query_model(**q_inputs)
    debug_trace(debug_enabled, "direct_query_side: doc frozen forward")
    with torch.autocast("cuda", dtype=torch.bfloat16):
        with torch.no_grad():
            _clear_rope_deltas(frozen_doc_model)
            d_emb = frozen_doc_model(**d_inputs)
    debug_trace(debug_enabled, "direct_query_side: loss backward")
    with torch.autocast("cuda", dtype=torch.bfloat16):
        loss, accuracy = clip_loss(
            q_emb,
            d_emb,
            logit_scale,
            gather_enabled=gather_enabled,
            hardness_alpha=hardness_alpha,
        )
        loss.backward()
    if dist.is_initialized():
        debug_trace(debug_enabled, "direct_query_side: manual all_reduce grads")
        manual_all_reduce_grads(query_model, logit_scale)
    debug_trace(debug_enabled, "direct_query_side: done")
    return loss.detach(), accuracy.detach()
