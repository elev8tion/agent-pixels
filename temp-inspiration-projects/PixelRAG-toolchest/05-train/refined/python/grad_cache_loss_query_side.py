def grad_cache_loss_query_side(
    query_model,
    frozen_doc_model,
    query_chunks,
    doc_chunks,
    logit_scale,
    query_process_fn,
    doc_process_fn,
    debug_enabled=False,
    hardness_alpha=0.0,
):
    """GradCache variant for query-only tuning with a frozen document tower."""
    raw_query_model = (
        query_model.module if hasattr(query_model, "module") else query_model
    )

    # Step 1: query embeddings come from the trainable tower; document embeddings
    # come from the frozen base tower so the datastore stays valid.
    debug_trace(debug_enabled, "gradcache_query_side: start query no-grad pass")
    query_embs, query_states = get_chunked_embeddings(
        query_model, query_chunks, query_process_fn
    )

    debug_trace(debug_enabled, "gradcache_query_side: start doc frozen pass")
    doc_embs = []
    with torch.autocast("cuda", dtype=torch.bfloat16):
        with torch.no_grad():
            for chunk in doc_chunks:
                doc_embs.append(doc_process_fn(frozen_doc_model, chunk))
    doc_embs = torch.cat(doc_embs, dim=0)

    # Step 2: compute loss and cache only the query-side gradients.
    debug_trace(
        debug_enabled, "gradcache_query_side: start loss backward on detached embs"
    )
    query_embs_d = query_embs.detach().requires_grad_()
    doc_embs_d = doc_embs.detach().requires_grad_()
    with torch.autocast("cuda", dtype=torch.bfloat16):
        loss, accuracy = clip_loss(
            query_embs_d,
            doc_embs_d,
            logit_scale,
            gather_enabled=True,
            hardness_alpha=hardness_alpha,
        )
        loss.backward()

    query_cache = query_embs_d.grad
    loss_val = loss.detach()

    # Step 3: replay only query chunks; doc tower is frozen and never backprops.
    q_chunk_sizes = [c["input_ids"].shape[0] for c in query_chunks]
    query_grad_chunks = query_cache.split(q_chunk_sizes)

    has_ddp = hasattr(query_model, "no_sync")
    debug_trace(debug_enabled, "gradcache_query_side: replay query chunks")
    for chunk, grad, state in zip(query_chunks, query_grad_chunks, query_states):
        sync_ctx = query_model.no_sync() if has_ddp else nullcontext()
        with sync_ctx:
            with torch.autocast("cuda", dtype=torch.bfloat16):
                with state:
                    emb = query_process_fn(raw_query_model, chunk)
                surrogate = torch.dot(emb.flatten(), grad.flatten())
            surrogate.backward()

    if has_ddp and dist.is_initialized():
        debug_trace(debug_enabled, "gradcache_query_side: manual all_reduce grads")
        manual_all_reduce_grads(query_model, logit_scale)
    debug_trace(debug_enabled, "gradcache_query_side: done")

    return loss_val, accuracy.detach()
