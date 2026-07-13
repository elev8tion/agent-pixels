@torch.no_grad()
def embed_query_texts(model, processor, queries, device, batch_size=128):
    """Embed text queries with the current query tower."""
    raw = model.module if hasattr(model, "module") else model
    all_embs = []
    for i in range(0, len(queries), batch_size):
        batch = queries[i : i + batch_size]
        inputs = process_queries(processor, batch)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.autocast("cuda", dtype=torch.bfloat16):
            _clear_rope_deltas(raw)
            emb = raw(**inputs, bidirectional=getattr(raw, "_bidirectional", False))
        all_embs.append(emb.cpu().float().numpy())
    if not all_embs:
        return np.zeros((0, 0), dtype=np.float32)
    return np.concatenate(all_embs, axis=0)
