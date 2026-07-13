@torch.no_grad()
    def clamp_(self):
        """Clamp log_scale in-place. Call after optimizer.step()."""
        self.log_scale.clamp_(0, self.max_log)
