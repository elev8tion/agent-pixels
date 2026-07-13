def compare_gradients(grads_ref, grads_gc, names, verbose=True):
    """Compare gradients. Returns (cosine, rel_l2, max_rel_diff)."""
    flat_ref, flat_gc = [], []
    max_rel = 0.0
    n_compared = 0

    if verbose:
        print(f"\n{'Parameter':<60} {'MaxDiff':>12} {'MeanDiff':>12} {'RelDiff':>12}")
        print("-" * 100)

    for name, gr, ggc in zip(names, grads_ref, grads_gc):
        if gr is None and ggc is None:
            continue
        if gr is None or ggc is None:
            print(f"  MISMATCH: {name} — one grad is None")
            return 0.0, float("inf"), float("inf")
        if gr.abs().max().item() == 0 and ggc.abs().max().item() == 0:
            continue

        flat_ref.append(gr.flatten())
        flat_gc.append(ggc.flatten())
        n_compared += 1

        abs_diff = (gr - ggc).abs()
        max_diff = abs_diff.max().item()
        mean_diff = abs_diff.mean().item()
        scale = gr.abs().mean().item()
        rel_diff = mean_diff / max(scale, 1e-12)
        max_rel = max(max_rel, rel_diff)

        if verbose:
            print(f"{name:<60} {max_diff:>12.6e} {mean_diff:>12.6e} {rel_diff:>12.6e}")

    if not flat_ref:
        print("No non-zero gradients to compare.")
        return 1.0, 0.0, 0.0

    ref_cat = torch.cat(flat_ref)
    gc_cat = torch.cat(flat_gc)
    cosine = F.cosine_similarity(ref_cat.unsqueeze(0), gc_cat.unsqueeze(0)).item()
    l2_diff = (ref_cat - gc_cat).norm().item()
    rel_l2 = l2_diff / max(ref_cat.norm().item(), 1e-12)

    if verbose:
        print(f"\nCompared {n_compared} parameter groups")
        print(f"  Cosine similarity:  {cosine:.10f}")
        print(f"  Relative L2 diff:   {rel_l2:.6e}")
        print(f"  Max per-param rel:  {max_rel:.6e}")

    return cosine, rel_l2, max_rel
