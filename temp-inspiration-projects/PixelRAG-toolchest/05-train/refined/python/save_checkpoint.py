def save_checkpoint(
    model, optimizer, scheduler, step, config, best_recall_10=0.0, loss_history=None
):
    """Save LoRA weights + optimizer/scheduler state."""
    ckpt_dir = Path(config.checkpoint_dir) / config.run_name
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    path = ckpt_dir / f"step_{step}.pt"
    torch.save(
        {
            "step": step,
            "model_state_dict": {k: v.cpu() for k, v in model.state_dict().items()},
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict(),
            "best_recall_10": best_recall_10,
            "loss_history": loss_history or [],
            "config": vars(config),
        },
        path,
    )
    _log(f"Checkpoint saved: {path}")
