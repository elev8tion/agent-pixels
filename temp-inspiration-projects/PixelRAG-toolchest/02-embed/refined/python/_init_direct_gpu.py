def _init_direct_gpu(
    model_path: str,
    gpu_id: int,
    enforce_eager: bool = False,
    adapter_path: str | None = None,
):
    """Load model + processor for direct GPU inference.

    Uses Qwen3VLForConditionalGeneration (not AutoModel, which loads the
    base Qwen3VLModel with uninitialized language_model weights).
    GPU-accelerated image preprocessing (device='cuda' in processor) avoids
    the CPU preprocessing bottleneck: 0.2s vs 12s per batch of 64.

    If adapter_path is given, loads a PEFT LoRA adapter and merges it into
    the base weights (merge_and_unload) so inference runs at base-model speed.
    """
    import torch
    from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

    processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    )

    if adapter_path:
        from peft import PeftModel, set_peft_model_state_dict
        from safetensors.torch import load_file as load_safetensors
        import re as _re

        logger.info("GPU %d: loading LoRA adapter from %s", gpu_id, adapter_path)
        # The adapter was trained on Qwen3VLModel (BiQwen3), where attention
        # layers live at language_model.layers.*.  But Qwen3VLForConditional-
        # Generation wraps that inside self.model, so PEFT expects an extra
        # "model." prefix.  Remap keys before loading.
        adapter_weights_path = os.path.join(adapter_path, "adapter_model.safetensors")
        raw_sd = load_safetensors(adapter_weights_path)
        remapped_sd = {}
        for k, v in raw_sd.items():
            # base_model.model.language_model.* -> base_model.model.model.language_model.*
            new_k = _re.sub(
                r"^(base_model\.model\.)(language_model\.|visual\.)", r"\1model.\2", k
            )
            remapped_sd[new_k] = v
        n_remapped = sum(
            1 for ok, nk in zip(raw_sd.keys(), remapped_sd.keys()) if ok != nk
        )
        logger.info(
            "GPU %d: remapped %d/%d adapter keys (BiQwen3 -> ConditionalGeneration)",
            gpu_id,
            n_remapped,
            len(raw_sd),
        )

        model = PeftModel.from_pretrained(model, adapter_path)
        set_peft_model_state_dict(model, remapped_sd)
        model = model.merge_and_unload()
        logger.info("GPU %d: LoRA merged into base weights", gpu_id)

    model = model.cuda().eval()

    # WORKAROUND: torch 2.9.x Conv3d bf16 bug (pytorch/pytorch#166122) —
    # cuDNN 9.8–9.14 disabled for 3D conv, vol2col fallback is 16,400x slower for bf16.
    # Fixed in cuDNN >= 9.15. Only apply fp32 workaround if needed.
    cudnn_ver = torch.backends.cudnn.version()
    if cudnn_ver < 91500:
        _pe = model.model.visual.patch_embed

        def _fp32_patch_embed(hidden_states, _pe=_pe):
            conv = _pe.proj
            x = hidden_states.view(
                -1,
                _pe.in_channels,
                _pe.temporal_patch_size,
                _pe.patch_size,
                _pe.patch_size,
            )
            old_w, old_b = conv.weight.data, conv.bias.data
            conv.weight.data = old_w.float()
            conv.bias.data = old_b.float()
            out = conv(x.float()).view(-1, _pe.embed_dim)
            conv.weight.data = old_w
            conv.bias.data = old_b
            return out.to(torch.bfloat16)

        _pe.forward = _fp32_patch_embed
        logger.info(f"Applied fp32 Conv3d workaround (cuDNN {cudnn_ver} < 91500)")
    else:
        logger.info(f"Native bf16 Conv3d (cuDNN {cudnn_ver} >= 91500, bug fixed)")

    return (model, processor)
