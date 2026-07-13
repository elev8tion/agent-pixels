def save_npz(path: str, compressed: bool, **arrays) -> None:
    """Save npz with optional compression."""
    if compressed:
        np.savez_compressed(path, **arrays)
    else:
        np.savez(path, **arrays)
