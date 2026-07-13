def test_hard_negative_labels():
    """Verify that hard negative interleaving produces equivalent loss.

    Contrastors: docs = [pos0, neg0a, neg0b, pos1, neg1a, neg1b]
                 labels = [0, 3] (positive positions in flattened doc array)
                 similarity = query @ docs.T, cross_entropy(sim, labels)

    Swift:       sentences = [[q0, pos0, neg0a, neg0b], [q1, pos1, neg1a, neg1b]]
                 split per sample, stack → [B, neg+2, D]
                 queries = sentences[:, 0], docs_all = sentences[:, 1:].reshape(-1, D)
                 labels = [0, 3] (start of each group's doc block)
                 similarity = queries @ docs_all.T, cross_entropy(sim / temp, labels)
    """
    print("\n=== Test 5: Hard negative label construction ===")

    import torch.nn.functional as F
    from train_contrastors import LogitScale

    torch.manual_seed(123)
    batch_size = 3
    num_hard_neg = 2
    dim = 64
    temperature = 0.07

    # Create normalized embeddings
    query_embs = torch.randn(batch_size, dim)
    query_embs = query_embs / query_embs.norm(dim=-1, keepdim=True)

    # docs_per_query = 1 pos + num_hard_neg
    docs_per_query = 1 + num_hard_neg
    all_doc_embs = torch.randn(batch_size * docs_per_query, dim)
    all_doc_embs = all_doc_embs / all_doc_embs.norm(dim=-1, keepdim=True)

    # --- Contrastors path ---
    # clip_loss: labels point to positive positions [0, 3, 6]
    logit_scale = LogitScale(init_value=1.0 / temperature)
    similarity_c = logit_scale(torch.matmul(query_embs, all_doc_embs.T))
    labels_c = torch.arange(batch_size) * docs_per_query
    contrastors_loss = F.cross_entropy(similarity_c, labels_c).item()

    # --- Swift path ---
    # Reconstruct swift's format: [B, neg+2, D] where dim1 = [query, pos, neg1, neg2]
    sentences = []
    for i in range(batch_size):
        group = torch.cat(
            [
                query_embs[i : i + 1],
                all_doc_embs[i * docs_per_query : (i + 1) * docs_per_query],
            ],
            dim=0,
        )  # [neg+2, D]
        sentences.append(group)
    sentences = torch.stack(sentences, dim=0)  # [B, neg+2, D]

    queries = sentences[:, 0]  # [B, D]
    docs_all = sentences[:, 1:].reshape(-1, dim)  # [B*(neg+1), D]
    labels_s = torch.arange(0, batch_size * (docs_per_query), docs_per_query)
    similarity_s = torch.matmul(queries, docs_all.T) / temperature
    swift_loss = F.cross_entropy(similarity_s, labels_s).item()

    diff = abs(contrastors_loss - swift_loss)
    print(f"  Contrastors loss (hard neg): {contrastors_loss:.6f}")
    print(f"  Swift loss (hard neg):       {swift_loss:.6f}")
    print(f"  Label contrastors: {labels_c.tolist()}")
    print(f"  Label swift:       {labels_s.tolist()}")
    print(f"  Absolute diff:     {diff:.6e}")

    assert diff < 1e-5, f"Hard negative loss mismatch: {diff}"
    print("  PASSED ✓")
    return True
