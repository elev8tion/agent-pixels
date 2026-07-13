def load_model_for_training(
    model_path: str,
    gpu_id: int,
    lora_r: int = 32,
    lora_alpha: int = 32,
    lora_dropout: float = 0.05,
):
    """Load Qwen3-VL with LoRA adapters for fine-tuning.

    Uses Qwen3VLForConditionalGeneration (NOT AutoModel, which loads
    Qwen3VLModel with random language_model weights).
    """
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        model_path,
        dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    lora_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=lora_dropout,
        task_type="FEATURE_EXTRACTION",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    device = f"cuda:{gpu_id}"
    model = model.to(device)
    return model
