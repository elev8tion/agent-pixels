def train(config):
    import wandb

    device = f"cuda:{config.gpu_id}"

    # wandb — disable console capture so logger output reaches stdout
    wandb.init(
        project="wiki-embedding",
        name=config.run_name,
        config=vars(config),
        settings=wandb.Settings(console="off"),
    )

    # Model
    _log(f"Loading model {config.model} on GPU {config.gpu_id}...")
    model = load_model_for_training(
        config.model,
        config.gpu_id,
        lora_r=config.lora_r,
        lora_alpha=config.lora_alpha,
    )
    processor = load_processor(
        config.model, min_pixels=config.min_pixels, max_pixels=config.max_pixels
    )

    # Data
    dataset = QueryChunkDataset(config.train_jsonl)
    collate_fn = make_collate_fn(processor, device=device)
    loader = DataLoader(
        dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=0,
        collate_fn=collate_fn,
    )

    # Optimizer + scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr, weight_decay=0.01)
    if config.scheduler == "cosine":
        scheduler = get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=config.warmup_steps,
            num_training_steps=config.max_steps,
        )
    else:
        scheduler = get_constant_schedule_with_warmup(
            optimizer,
            num_warmup_steps=config.warmup_steps,
        )

    # Resume
    start_step = 0
    best_recall_10 = 0.0
    loss_history = []
    if config.resume:
        _log(f"Resuming from {config.resume}")
        ckpt = torch.load(config.resume, map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model_state_dict"], strict=False)
        optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        scheduler.load_state_dict(ckpt["scheduler_state_dict"])
        start_step = ckpt["step"]
        best_recall_10 = ckpt.get("best_recall_10", 0.0)
        loss_history = ckpt.get("loss_history", [])
        _log(f"Resumed from step {start_step}")

    # Graceful shutdown
    shutdown = threading.Event()
    original_sigterm = signal.getsignal(signal.SIGTERM)
    original_sigint = signal.getsignal(signal.SIGINT)

    def _shutdown_handler(signum, frame):
        _log(f"Received signal {signum}, shutting down gracefully...")
        shutdown.set()

    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)

    # Train loop
    step = start_step
    model.train()
    skipped_batches = 0

    _log(f"Starting training from step {step}, max_steps={config.max_steps}")

    try:
        while step < config.max_steps:
            for batch in loader:
                if shutdown.is_set():
                    _log("Shutdown requested, saving checkpoint...")
                    save_checkpoint(
                        model,
                        optimizer,
                        scheduler,
                        step,
                        config,
                        best_recall_10,
                        loss_history,
                    )
                    wandb.finish()
                    return

                if batch is None:
                    skipped_batches += 1
                    wandb.log({"skipped_batches": skipped_batches}, step=step)
                    continue

                t0 = time.time()
                try:
                    q_inputs, i_inputs = batch

                    # Forward: query embeddings
                    q_out = model(**q_inputs, output_hidden_states=True)
                    q_emb = pool_and_normalize(
                        q_out.hidden_states[-1], q_inputs["attention_mask"]
                    )

                    # Forward: image embeddings
                    i_out = model(**i_inputs, output_hidden_states=True)
                    i_emb = pool_and_normalize(
                        i_out.hidden_states[-1], i_inputs["attention_mask"]
                    )

                    loss = info_nce_loss(q_emb, i_emb, temperature=config.temperature)
                    loss.backward()
                    clip_grad_norm_(model.parameters(), 1.0)
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()

                except torch.cuda.OutOfMemoryError:
                    _log(f"WARNING OOM at step {step}, skipping batch")
                    torch.cuda.empty_cache()
                    optimizer.zero_grad()
                    skipped_batches += 1
                    wandb.log({"skipped_batches": skipped_batches}, step=step)
                    continue

                dt = time.time() - t0
                step += 1
                loss_val = loss.item()
                loss_history.append(loss_val)
                lr = scheduler.get_last_lr()[0]
                gpu_mem = torch.cuda.memory_allocated(config.gpu_id) / 1e9

                wandb.log(
                    {
                        "loss": loss_val,
                        "lr": lr,
                        "batch_time": dt,
                        "pairs_per_sec": config.batch_size / dt,
                        "gpu_mem_gb": gpu_mem,
                    },
                    step=step,
                )
                _log(
                    f"step={step} loss={loss_val:.4f} lr={lr:.2e} "
                    f"batch_time={dt:.1f}s pairs/s={config.batch_size / dt:.1f} "
                    f"gpu_mem={gpu_mem:.1f}GB"
                )

                # Eval
                if step % config.eval_every == 0:
                    r1, r10, mrr = run_eval(
                        model,
                        processor,
                        config.eval_jsonl,
                        device,
                        batch_size=config.batch_size,
                    )
                    wandb.log(
                        {
                            "recall@1": r1,
                            "recall@10": r10,
                            "mrr": mrr,
                        },
                        step=step,
                    )
                    _log(
                        f"eval step={step} recall@1={r1:.3f} recall@10={r10:.3f} mrr={mrr:.3f}"
                    )
                    if r10 > best_recall_10:
                        best_recall_10 = r10

                # Checkpoint
                if step % config.save_every == 0:
                    save_checkpoint(
                        model,
                        optimizer,
                        scheduler,
                        step,
                        config,
                        best_recall_10,
                        loss_history,
                    )

                if step >= config.max_steps:
                    break

    finally:
        # Restore signal handlers
        signal.signal(signal.SIGTERM, original_sigterm)
        signal.signal(signal.SIGINT, original_sigint)

    # Final checkpoint
    save_checkpoint(
        model, optimizer, scheduler, step, config, best_recall_10, loss_history
    )
    wandb.finish()
    _log("Training complete!")
