def grad_cache_loss(
    model,
    query_chunks,
    doc_chunks,
    logit_scale,
    query_process_fn,
    doc_process_fn,
    hardness_alpha=0.0,
    loss_fn=None,
):
    """GradCache: large effective batch with constant memory (from contrastors/loss.py).

    1. Forward all chunks WITHOUT grad → cache embeddings
    2. Compute loss on full gathered embeddings → cache gradients
    3. Replay forward WITH grad, backprop through surrogate loss

    All surrogate backward passes run under no_sync(), then we manually
    all_reduce gradients for both the model and logit_scale.
    """
    if loss_fn is None:
        loss_fn = clip_loss
    raw_model = model.module if hasattr(model, "module") else model

    # Step 1: get all embeddings without grad (no DDP involvement)
    query_embs, query_states = get_chunked_embeddings(
        model, query_chunks, query_process_fn
    )
    doc_embs, doc_states = get_chunked_embeddings(model, doc_chunks, doc_process_fn)

    # Step 2: compute loss, get gradient w.r.t. embeddings
    # This uses all_gather (NCCL collective #1) and its backward does
    # reduce_scatter (NCCL collective #2). Both happen on detached tensors,
    # NOT through DDP, so DDP doesn't interfere.
    query_embs_d = query_embs.detach().requires_grad_()
    doc_embs_d = doc_embs.detach().requires_grad_()

    with torch.autocast("cuda", dtype=torch.bfloat16):
        loss, accuracy = loss_fn(
            query_embs_d,
            doc_embs_d,
            logit_scale,
            gather_enabled=True,
            hardness_alpha=hardness_alpha,
        )
        loss.backward()

    query_cache = query_embs_d.grad
    doc_cache = doc_embs_d.grad
    loss_val = loss.detach()

    # Step 3: accumulate real gradients via surrogate loss
    # Combine all chunks into a single list so DDP sync happens exactly ONCE
    # (on the very last backward call). This matches contrastors' pattern.
    # Split grad cache to match the actual chunk sizes (doc may differ from query
    # when hard negatives are used — doc batch = query_batch * (1+num_hard_neg))
    q_chunk_sizes = [c["input_ids"].shape[0] for c in query_chunks]
    d_chunk_sizes = [c["input_ids"].shape[0] for c in doc_chunks]
    query_grad_chunks = query_cache.split(q_chunk_sizes)
    doc_grad_chunks = doc_cache.split(d_chunk_sizes)

    all_chunks = list(query_chunks) + list(doc_chunks)
    all_grads = list(query_grad_chunks) + list(doc_grad_chunks)
    all_states = list(query_states) + list(doc_states)
    all_fns = [query_process_fn] * len(query_chunks) + [doc_process_fn] * len(
        doc_chunks
    )

    # All backward calls use no_sync to avoid DDP reducer confusion (query chunks
    # skip visual encoder while doc chunks use it → different "used" parameter sets
    # across chunks causes intermittent NCCL deadlocks with find_unused_parameters).
    # We manually all_reduce gradients after all backward calls.
    has_ddp = hasattr(model, "no_sync")
    for chunk, grad, state, fn in zip(all_chunks, all_grads, all_states, all_fns):
        sync_ctx = model.no_sync() if has_ddp else nullcontext()
        with sync_ctx:
            with torch.autocast("cuda", dtype=torch.bfloat16):
                with state:
                    emb = fn(raw_model, chunk)
                surrogate = torch.dot(emb.flatten(), grad.flatten())
            surrogate.backward()

    # Manual gradient all_reduce (replaces DDP's built-in sync).
    # Always call all_reduce on every requires_grad param (fill zero grad if None)
    # to ensure all ranks issue the same number of NCCL collectives — prevents
    # deadlocks if different chunks produce gradients on different param subsets.
    if has_ddp and dist.is_initialized():
        manual_all_reduce_grads(model, logit_scale)

    return loss_val, accuracy.detach()
