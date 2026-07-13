def run_test(
    label,
    model,
    model_state,
    ls_state,
    query_inputs,
    doc_inputs,
    chunk_size,
    device,
    verbose=True,
):
    """Compare chunked-reference vs GradCache for a given chunk_size."""

    # --- Chunked reference (full-memory backward) ---
    model.load_state_dict(model_state)
    ls_ref = LogitScale(init_value=1 / 0.07).to(device)
    ls_ref.load_state_dict(ls_state)
    model.zero_grad()
    ls_ref.zero_grad()

    # Create fresh chunks for each path (can't share autograd graphs)
    q_chunks_ref = chunk_inputs(
        {k: v.clone() for k, v in query_inputs.items()}, chunk_size
    )
    d_chunks_ref = chunk_inputs(
        {k: v.clone() for k, v in doc_inputs.items()}, chunk_size
    )

    # Seed before reference forward so dropout masks are deterministic
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    loss_ref, _ = chunked_reference_forward_backward(
        model, q_chunks_ref, d_chunks_ref, ls_ref
    )
    names, grads_ref = collect_grads(model, ls_ref)

    # --- GradCache (actual function from train_contrastors.py) ---
    model.load_state_dict(model_state)
    ls_gc = LogitScale(init_value=1 / 0.07).to(device)
    ls_gc.load_state_dict(ls_state)
    model.zero_grad()
    ls_gc.zero_grad()

    q_chunks_gc = chunk_inputs(
        {k: v.clone() for k, v in query_inputs.items()}, chunk_size
    )
    d_chunks_gc = chunk_inputs(
        {k: v.clone() for k, v in doc_inputs.items()}, chunk_size
    )

    # Same seed → GradCache step 1 (no-grad forward) uses the same dropout masks
    # as the reference. Step 3 (replay) uses RandContext to reproduce them.
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    loss_gc, acc_gc = grad_cache_loss(
        model=model,
        query_chunks=q_chunks_gc,
        doc_chunks=d_chunks_gc,
        logit_scale=ls_gc,
        query_process_fn=forward_query,
        doc_process_fn=forward_doc,
    )
    _, grads_gc = collect_grads(model, ls_gc)

    if verbose:
        print(f"\n  Loss reference: {loss_ref.item():.8f}")
        print(f"  Loss GradCache: {loss_gc.item():.8f}")
        print(f"  Loss diff:      {abs(loss_ref.item() - loss_gc.item()):.2e}")

    cosine, rel_l2, max_rel = compare_gradients(
        grads_ref, grads_gc, names, verbose=verbose
    )
    return cosine, rel_l2, loss_ref.item(), loss_gc.item()
