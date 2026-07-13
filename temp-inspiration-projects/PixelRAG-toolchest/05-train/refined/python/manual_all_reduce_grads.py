def manual_all_reduce_grads(*modules):
    """Average gradients across ranks for modules outside DDP's reducer path."""
    for module in modules:
        for param in module.parameters():
            if not param.requires_grad:
                continue
            if param.grad is None:
                param.grad = torch.zeros_like(param)
            dist.all_reduce(param.grad, op=dist.ReduceOp.AVG)
