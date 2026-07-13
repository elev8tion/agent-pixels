def test_training_step():
    """Run one training step through both pipelines and compare loss.

    Uses the same model weights, same data, same hyperparameters.
    Compares the loss value after one forward pass (no grad, just loss).
    """
    print("\n=== Test 7: Training step loss equivalence ===")

    from PIL import Image
    from transformers import AutoProcessor
    from models.biqwen3 import BiQwen3
    from train_contrastors import (
        init_chat_templates,
        process_queries,
        process_doc_images,
        LogitScale,
        clip_loss,
        _clear_rope_deltas,
    )

    temperature = 0.07
    num_hard_neg = 2

    # Load 2 samples
    with open("data/train_hn.jsonl") as f:
        samples = [json.loads(f.readline()) for _ in range(2)]

    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    processor.tokenizer.padding_side = "left"
    init_chat_templates(processor)

    # Prepare data
    queries = [s["query"] for s in samples]
    doc_images = []
    for s in samples:
        doc_images.append(Image.open(s["chunk_path"]).convert("RGB"))
        neg_paths = s.get("neg_chunk_paths", [])
        for np_ in neg_paths[:num_hard_neg]:
            if np_ and os.path.exists(np_):
                doc_images.append(Image.open(np_).convert("RGB"))

    q_inputs = process_queries(processor, queries)
    d_inputs = process_doc_images(processor, doc_images)

    # --- Contrastors loss ---
    model = BiQwen3.from_pretrained(MODEL_NAME, dtype=torch.bfloat16).cuda().eval()
    q_inputs_c = {k: v.cuda() for k, v in q_inputs.items()}
    d_inputs_c = {k: v.cuda() for k, v in d_inputs.items()}

    logit_scale = LogitScale(init_value=1.0 / temperature).cuda()

    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        _clear_rope_deltas(model)
        q_emb = model(**q_inputs_c)
        _clear_rope_deltas(model)
        d_emb = model(**d_inputs_c)
        c_loss, c_acc = clip_loss(q_emb, d_emb, logit_scale, gather_enabled=False)

    contrastors_loss = c_loss.item()
    contrastors_acc = c_acc.item()

    # Extract embeddings for swift comparison
    q_emb_np = q_emb.cpu().float()
    d_emb_np = d_emb.cpu().float()

    del model
    torch.cuda.empty_cache()

    # --- Swift loss (using the same embeddings) ---
    # Swift data layout:
    #   sentences: [anchor0, pos0, neg0a, neg0b, anchor1, pos1, neg1a, neg1b]
    #              = B * (1 anchor + 1 pos + num_neg) entries
    #   labels:    [1, 0, 0, 1, 0, 0]
    #              = B * (1 pos + num_neg) entries (anchors NOT in labels)
    #   The '1' marks positive positions. _parse_multi_negative_sentences uses
    #   an offset adjustment (+range) to account for anchors in sentences.
    docs_per_query = 1 + num_hard_neg
    batch_size = len(queries)

    swift_sentences = []
    swift_labels = []
    for i in range(batch_size):
        swift_sentences.append(q_emb_np[i])  # anchor (not in labels)
        swift_sentences.append(d_emb_np[i * docs_per_query])  # positive
        swift_labels.append(1.0)
        for j in range(1, docs_per_query):  # negatives
            swift_sentences.append(d_emb_np[i * docs_per_query + j])
            swift_labels.append(0.0)

    swift_sentences = torch.stack(swift_sentences, dim=0)  # [B*(1+1+num_neg), D]
    swift_labels = torch.tensor(swift_labels)  # [B*(1+num_neg)]

    # Run swift's parsing + InfoNCE logic (batched path, use_batch=True)
    from swift.loss.embedding import _parse_multi_negative_sentences

    split_tensors = _parse_multi_negative_sentences(
        swift_sentences, swift_labels, hard_negatives=num_hard_neg
    )

    # Each split_tensor = [anchor, pos, neg1, neg2] shape [neg+2, D]
    sentences_stacked = torch.stack(split_tensors, dim=0)  # [B, neg+2, D]
    swift_queries = sentences_stacked[:, 0]  # [B, D]
    docs_all = sentences_stacked[:, 1:].reshape(
        -1, sentences_stacked.size(2)
    )  # [B*(neg+1), D]
    swift_label_indices = torch.arange(0, batch_size * docs_per_query, docs_per_query)
    similarity = torch.matmul(swift_queries, docs_all.T) / temperature
    swift_loss = torch.nn.functional.cross_entropy(
        similarity, swift_label_indices
    ).item()

    diff = abs(contrastors_loss - swift_loss)
    print(f"  Contrastors loss: {contrastors_loss:.6f}  acc: {contrastors_acc:.4f}")
    print(f"  Swift loss:       {swift_loss:.6f}")
    print(f"  Absolute diff:    {diff:.6e}")
    print(
        f"  Batch: {batch_size} queries, {len(doc_images)} docs ({num_hard_neg} hard neg/query)"
    )

    for img in doc_images:
        img.close()

    # Allow small tolerance for bf16 accumulated differences
    assert diff < 0.01, f"Training step loss mismatch: {diff}"
    print("  PASSED ✓")
    return True
