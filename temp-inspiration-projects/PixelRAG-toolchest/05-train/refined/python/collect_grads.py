def collect_grads(model, logit_scale):
    names, grads = [], []
    for n, p in model.named_parameters():
        if p.requires_grad:
            names.append(n)
            grads.append(p.grad.clone().float() if p.grad is not None else None)
    for n, p in logit_scale.named_parameters():
        names.append(f"logit_scale.{n}")
        grads.append(p.grad.clone().float() if p.grad is not None else None)
    return names, grads
