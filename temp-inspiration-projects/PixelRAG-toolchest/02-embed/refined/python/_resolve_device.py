def _resolve_device(device: str) -> str:
    """Resolve device string, auto-detecting MPS on macOS."""
    import torch

    if device == "auto":
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    return device
