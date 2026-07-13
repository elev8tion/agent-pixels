class LogitScale(torch.nn.Module):
    """Learnable logit scale (from contrastors/OpenCLIP).

    Contrastors uses a learnable log-scale initialized to ln(1/0.07) ≈ 2.66.
    The parameter is clamped in-place AFTER optimizer.step() (not in forward),
    matching contrastors' approach. Clamping in forward would create a dead zone
    where gradients are zero when log_scale exceeds the limit.
    """

    def __init__(self, init_value=1 / 0.07, max_value=100.0):
        super().__init__()
        self.log_scale = torch.nn.Parameter(torch.log(torch.tensor(init_value)))
        self.max_log = float(torch.log(torch.tensor(max_value)))

    def forward(self, x):
        return x * self.log_scale.exp()

    @torch.no_grad()
    def clamp_(self):
        """Clamp log_scale in-place. Call after optimizer.step()."""
        self.log_scale.clamp_(0, self.max_log)
