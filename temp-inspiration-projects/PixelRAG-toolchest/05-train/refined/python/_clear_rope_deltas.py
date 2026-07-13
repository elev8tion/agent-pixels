def _clear_rope_deltas(model):
    """Clear stale rope_deltas state on Qwen3VL model.

    Qwen3VLModel.compute_3d_position_ids stores self.rope_deltas after processing
    image batches. On subsequent text-only forwards, it reuses this stale state,
    causing shape mismatch: position_ids (3, batch, seq_len) + delta (old_batch, 1).
    Must clear between image→text forward transitions.
    """
    inner = model
    # Unwrap PeftModel → BiQwen3 → Qwen3VLModel
    while hasattr(inner, "model"):
        inner = inner.model
    if hasattr(inner, "rope_deltas"):
        inner.rope_deltas = None
