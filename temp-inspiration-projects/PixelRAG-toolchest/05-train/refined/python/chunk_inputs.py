def chunk_inputs(inputs, chunk_size):
    """Split a batch of inputs into chunks along batch dimension.

    Only includes tensor values in chunks (non-tensors are dropped) so that
    RandContext's get_device_states doesn't crash on non-tensor dict values.
    """
    batch_size = next(
        v.shape[0] for v in inputs.values() if isinstance(v, torch.Tensor)
    )
    # Verify all tensors are batch-major (first dim == batch_size).
    # pixel_values must be (B, max_patches, dim), not flattened (sum_patches, dim).
    for k, v in inputs.items():
        if isinstance(v, torch.Tensor) and v.shape[0] != batch_size:
            raise ValueError(
                f"chunk_inputs: {k}.shape[0]={v.shape[0]} != batch_size={batch_size}. "
                f"All tensors must be batch-major for chunking."
            )
    chunks = []
    for start in range(0, batch_size, chunk_size):
        chunk = {
            k: v[start : start + chunk_size]
            for k, v in inputs.items()
            if isinstance(v, torch.Tensor)
        }
        chunks.append(chunk)
    return chunks
