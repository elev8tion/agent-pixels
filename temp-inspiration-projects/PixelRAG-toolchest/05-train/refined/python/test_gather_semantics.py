def test_gather_semantics():
    """Verify that gather_with_grad and gather_object produce the same
    forward-pass result on single GPU (no actual distributed).

    The key semantic difference:
    - contrastors gather_with_grad: gradients flow through all gathered tensors
    - swift gather_object: other ranks' tensors are detached

    On single GPU (world_size=1), both are no-ops. This test verifies that
    the loss computation (which uses gathered embeddings) is identical when
    there's only one "rank", confirming the single-GPU equivalence.

    Multi-GPU difference: contrastors gives slightly different gradients because
    gradients flow through all ranks' embeddings. This test documents the known
    difference but cannot verify it without multiple GPUs.
    """
    print("\n=== Test 8: Cross-GPU gather semantics ===")

    import torch.nn.functional as F
    from train_contrastors import LogitScale, clip_loss, gather_with_grad

    torch.manual_seed(99)
    batch_size = 4
    dim = 64
    temperature = 0.07

    q = torch.randn(batch_size, dim)
    q = q / q.norm(dim=-1, keepdim=True)
    d = torch.randn(batch_size, dim)
    d = d / d.norm(dim=-1, keepdim=True)

    # contrastors path (gather_enabled=False on single GPU is equivalent)
    logit_scale = LogitScale(init_value=1.0 / temperature)
    loss_c, _ = clip_loss(q, d, logit_scale, gather_enabled=False)

    # Simulate gather_with_grad on single GPU (should be identity)
    d_gathered = gather_with_grad(d)
    sim = logit_scale(torch.matmul(q, d_gathered.T))
    labels = torch.arange(batch_size)
    loss_gathered = F.cross_entropy(sim, labels)

    # swift path
    sim_s = torch.matmul(q, d.T) / temperature
    loss_swift = F.cross_entropy(sim_s, labels)

    diff_cg = abs(loss_c.item() - loss_gathered.item())
    diff_cs = abs(loss_c.item() - loss_swift.item())

    print(f"  clip_loss (no gather):    {loss_c.item():.6f}")
    print(f"  clip_loss (w/ gather):    {loss_gathered.item():.6f}")
    print(f"  swift (/ temperature):    {loss_swift.item():.6f}")
    print(f"  Diff (no gather vs gather):       {diff_cg:.6e}")
    print(f"  Diff (contrastors vs swift):      {diff_cs:.6e}")
    print("  NOTE: Multi-GPU gradient difference (gather_with_grad vs detached gather)")
    print(
        "         cannot be tested without multiple GPUs. This is a KNOWN difference."
    )

    assert diff_cg < 1e-6, f"gather_with_grad changed loss on single GPU: {diff_cg}"
    assert diff_cs < 1e-5, f"Loss diverged: {diff_cs}"
    print("  PASSED ✓")
    return True
