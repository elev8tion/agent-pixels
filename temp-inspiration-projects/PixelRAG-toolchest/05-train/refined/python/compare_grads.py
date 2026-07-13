def compare_grads(grads_a, grads_b, names):
    """Compare gradients, return cosine similarity."""
    flat_a, flat_b = [], []
    for name, ga, gb in zip(names, grads_a, grads_b):
        if ga is None and gb is None:
            continue
        if ga is None or gb is None:
            return 0.0  # mismatch
        if ga.abs().max().item() == 0 and gb.abs().max().item() == 0:
            continue
        flat_a.append(ga.flatten())
        flat_b.append(gb.flatten())

    if not flat_a:
        return 1.0

    a = torch.cat(flat_a)
    b = torch.cat(flat_b)
    cosine = F.cosine_similarity(a.unsqueeze(0), b.unsqueeze(0)).item()
    rel_l2 = (a - b).norm().item() / max(a.norm().item(), 1e-12)
    return cosine, rel_l2
