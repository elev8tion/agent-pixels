def test_lora_targets():
    """Verify LoRA is applied to the same parameters."""
    print("\n=== Test 4: LoRA target equivalence ===")

    from models.biqwen3 import BiQwen3
    from peft import LoraConfig, get_peft_model

    model = BiQwen3.from_pretrained(MODEL_NAME, dtype=torch.bfloat16)
    lora_config = LoraConfig(
        r=32,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        task_type="FEATURE_EXTRACTION",
    )
    peft_model = get_peft_model(model, lora_config)

    contrastors_trainable = sorted(
        [n for n, p in peft_model.named_parameters() if p.requires_grad]
    )

    del peft_model, model
    torch.cuda.empty_cache()

    # Swift path: same LoRA config on ConditionalGeneration
    from transformers import Qwen3VLForConditionalGeneration

    swift_model = Qwen3VLForConditionalGeneration.from_pretrained(
        MODEL_NAME, torch_dtype=torch.bfloat16
    )
    swift_lora_config = LoraConfig(
        r=32,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        task_type="FEATURE_EXTRACTION",
    )
    swift_peft = get_peft_model(swift_model, swift_lora_config)

    swift_trainable = sorted(
        [n for n, p in swift_peft.named_parameters() if p.requires_grad]
    )

    del swift_peft, swift_model

    # Compare — swift has "model.model." prefix, contrastors has "model."
    # Normalize by stripping model prefixes
    def normalize_name(n):
        # Remove peft wrapper prefix
        n = n.replace("base_model.model.", "")
        # Remove the extra "model." from ConditionalGeneration
        if n.startswith("model."):
            n = n[len("model.") :]
        return n

    contrastors_normalized = sorted(
        set(normalize_name(n) for n in contrastors_trainable)
    )
    swift_normalized = sorted(set(normalize_name(n) for n in swift_trainable))

    # Check for lm_head LoRA in swift (shouldn't be there since q/k/v/o only)
    swift_lmhead = [n for n in swift_trainable if "lm_head" in n]

    only_contrastors = set(contrastors_normalized) - set(swift_normalized)
    only_swift = set(swift_normalized) - set(contrastors_normalized)

    print(f"  Contrastors trainable params: {len(contrastors_trainable)}")
    print(f"  Swift trainable params:       {len(swift_trainable)}")
    print(f"  Normalized contrastors:       {len(contrastors_normalized)}")
    print(f"  Normalized swift:             {len(swift_normalized)}")
    print(f"  Swift lm_head LoRA:           {len(swift_lmhead)} (should be 0)")

    if only_contrastors:
        print(f"  Only in contrastors: {list(only_contrastors)[:5]}...")
    if only_swift:
        print(f"  Only in swift: {list(only_swift)[:5]}...")

    match = contrastors_normalized == swift_normalized
    print(f"  Exact match: {match}")

    assert match, "LoRA targets differ!"
    assert len(swift_lmhead) == 0, "Swift has LoRA on lm_head!"
    print("  PASSED ✓")
    return True
