def embed_queries(model, processor, queries, batch_size=16):
    all_embs = []
    for i in range(0, len(queries), batch_size):
        batch = queries[i : i + batch_size]
        inputs = _process_queries(processor, batch)
        inputs = {k: v.cuda() for k, v in inputs.items()}
        with torch.no_grad():
            embs = model(**inputs)
        all_embs.append(embs.cpu().float().numpy())
    return np.concatenate(all_embs, axis=0)
