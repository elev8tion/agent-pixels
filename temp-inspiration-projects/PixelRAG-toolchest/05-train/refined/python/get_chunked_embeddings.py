def get_chunked_embeddings(model, chunks, process_fn):
    """Forward pass on chunks without grad, caching embeddings + RNG states."""
    embeddings = []
    rand_states = []
    # Use the unwrapped model for no-grad forward (avoids DDP overhead)
    raw_model = model.module if hasattr(model, "module") else model
    with torch.autocast("cuda", dtype=torch.bfloat16):
        with torch.no_grad():
            for chunk in chunks:
                rand_states.append(RandContext(chunk))
                emb = process_fn(raw_model, chunk)
                embeddings.append(emb)
    return torch.cat(embeddings, dim=0), rand_states
