def test_multi_gpu_gather():
    """Compare gradients from gather_with_grad vs detached gather on 2 GPUs.

    gather_with_grad: backward flows through all ranks' embeddings
    detached gather:  backward only flows through local rank's embeddings

    The LOSS should be identical (same forward computation).
    The GRADIENTS will differ because gather_with_grad lets rank 0's loss
    update rank 1's parameters (and vice versa) via reduce_scatter.

    Run with: CUDA_VISIBLE_DEVICES=1,2 torchrun --nproc_per_node=2 tests/test_swift_equivalence.py --multi-gpu
    """
    print("\n=== Test 9: Multi-GPU gather gradient difference ===")

    import torch.distributed as dist

    if not dist.is_initialized():
        dist.init_process_group("nccl")

    rank = dist.get_rank()
    world_size = dist.get_world_size()
    device = torch.device(f"cuda:{rank}")
    torch.cuda.set_device(device)

    assert world_size == 2, f"This test requires exactly 2 GPUs, got {world_size}"

    from train_contrastors import gather_with_grad

    torch.manual_seed(42 + rank)  # different data per rank
    batch_size = 4
    dim = 64
    temperature = 0.07

    # Each rank has its own query and doc embeddings
    q = torch.randn(batch_size, dim, device=device, requires_grad=True)
    q_norm = q / q.norm(dim=-1, keepdim=True)

    d = torch.randn(batch_size, dim, device=device, requires_grad=True)
    d_norm = d / d.norm(dim=-1, keepdim=True)

    # --- Path A: gather_with_grad (contrastors) ---
    d_gathered_grad = gather_with_grad(d_norm)  # [B*W, D], grad flows through all
    sim_a = torch.matmul(q_norm, d_gathered_grad.T) / temperature
    labels_a = torch.arange(batch_size, device=device) + rank * batch_size
    loss_a = torch.nn.functional.cross_entropy(sim_a, labels_a)
    loss_a.backward()
    grad_a_q = q.grad.clone()
    grad_a_d = d.grad.clone()

    # Reset grads
    q.grad = None
    d.grad = None

    # Recompute normalized (grad graph was consumed)
    q_norm2 = q / q.norm(dim=-1, keepdim=True)
    d_norm2 = d / d.norm(dim=-1, keepdim=True)

    # --- Path B: detached gather (swift-style) ---
    all_d = [torch.zeros_like(d_norm2) for _ in range(world_size)]
    dist.all_gather(all_d, d_norm2)
    # Detach other ranks, keep local with grad
    all_d[rank] = d_norm2
    for i in range(world_size):
        if i != rank:
            all_d[i] = all_d[i].detach()
    d_gathered_detach = torch.cat(all_d, dim=0)

    sim_b = torch.matmul(q_norm2, d_gathered_detach.T) / temperature
    labels_b = torch.arange(batch_size, device=device) + rank * batch_size
    loss_b = torch.nn.functional.cross_entropy(sim_b, labels_b)
    loss_b.backward()
    grad_b_q = q.grad.clone()
    grad_b_d = d.grad.clone()

    # Compare
    loss_diff = abs(loss_a.item() - loss_b.item())
    q_grad_cosine = torch.nn.functional.cosine_similarity(
        grad_a_q.flatten().unsqueeze(0), grad_b_q.flatten().unsqueeze(0)
    ).item()
    d_grad_cosine = torch.nn.functional.cosine_similarity(
        grad_a_d.flatten().unsqueeze(0), grad_b_d.flatten().unsqueeze(0)
    ).item()
    q_grad_diff = (grad_a_q - grad_b_q).abs().max().item()
    d_grad_diff = (grad_a_d - grad_b_d).abs().max().item()

    if rank == 0:
        print(f"  Loss diff (should be ~0):          {loss_diff:.6e}")
        print(f"  Query grad cosine:                  {q_grad_cosine:.6f}")
        print(f"  Doc grad cosine:                    {d_grad_cosine:.6f}")
        print(f"  Query grad max diff:                {q_grad_diff:.6e}")
        print(f"  Doc grad max diff:                  {d_grad_diff:.6e}")
        print("  NOTE: Gradient difference is EXPECTED and KNOWN.")
        print("         gather_with_grad propagates grad to all ranks' embeddings;")
        print("         detached gather only propagates to local rank.")

        # Loss should be identical (same forward)
        assert loss_diff < 1e-5, f"Loss should be identical: {loss_diff}"

        # Query grads should be identical (query is always local)
        assert q_grad_cosine > 0.999, (
            f"Query grads diverged unexpectedly: {q_grad_cosine}"
        )

        # Doc grads WILL differ — this is the known semantic difference
        # gather_with_grad: d gets gradient from all ranks' CE losses
        # detached gather: d only gets gradient from local rank's CE loss
        # We just document how much they differ
        print("\n  Doc grad difference quantifies the gather_with_grad vs detach gap.")
        print("  This is the ONLY non-equivalent component between the two pipelines.")

    dist.barrier()
    if rank == 0:
        print("  PASSED ✓")
    dist.destroy_process_group()
    return True
