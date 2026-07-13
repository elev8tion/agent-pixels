def test_loss():
    """Verify InfoNCE loss computation is equivalent."""
    print("\n=== Test 3: Loss equivalence ===")

    # Create synthetic embeddings (deterministic)
    torch.manual_seed(42)
    batch_size = 4
    dim = 128
    temperature = 0.07

    query_embs = torch.randn(batch_size, dim)
    query_embs = query_embs / query_embs.norm(dim=-1, keepdim=True)
    doc_embs = torch.randn(batch_size, dim)
    doc_embs = doc_embs / doc_embs.norm(dim=-1, keepdim=True)

    # --- Contrastors path: clip_loss ---
    from train_contrastors import LogitScale
    import torch.nn.functional as F

    logit_scale = LogitScale(init_value=1.0 / temperature)
    similarity = logit_scale(torch.matmul(query_embs, doc_embs.T))
    labels = torch.arange(batch_size)
    contrastors_loss = F.cross_entropy(similarity, labels).item()

    # --- Swift path: InfoNCE ---
    # Swift computes: similarity / temperature, then cross_entropy
    swift_similarity = torch.matmul(query_embs, doc_embs.T) / temperature
    swift_loss = F.cross_entropy(swift_similarity, labels).item()

    diff = abs(contrastors_loss - swift_loss)
    print(f"  Contrastors loss: {contrastors_loss:.6f}")
    print(f"  Swift loss:       {swift_loss:.6f}")
    print(f"  Absolute diff:    {diff:.6e}")

    # They should be identical: logit_scale(x) = x * exp(ln(1/0.07)) = x / 0.07
    assert diff < 1e-5, f"Loss mismatch: {diff}"
    print("  PASSED ✓")
    return True
