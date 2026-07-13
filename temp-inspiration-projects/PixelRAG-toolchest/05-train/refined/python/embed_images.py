def embed_images(model, processor, images, batch_size=8):
    all_embs = []
    for i in range(0, len(images), batch_size):
        batch = images[i : i + batch_size]
        inputs = _process_doc_images(processor, batch)
        inputs = {k: v.cuda() for k, v in inputs.items()}
        with torch.no_grad():
            embs = model(**inputs)
        all_embs.append(embs.cpu().float().numpy())
    return np.concatenate(all_embs, axis=0)
