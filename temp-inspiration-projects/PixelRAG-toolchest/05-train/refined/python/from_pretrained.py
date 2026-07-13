@classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, *args, **kwargs):
        # For transformers <5.0: handle key remapping manually
        from transformers import PreTrainedModel
        import inspect

        sig = inspect.signature(PreTrainedModel.from_pretrained)
        if "key_mapping" in sig.parameters:
            # transformers >=5.0: use native key_mapping
            kwargs.setdefault(
                "key_mapping",
                {
                    r"^model\.visual": "visual",
                    r"^model\.language_model": "language_model",
                    r"^model\.": "",
                },
            )
            return super().from_pretrained(
                pretrained_model_name_or_path, *args, **kwargs
            )

        # transformers <5.0: load with remapped state_dict
        from transformers import AutoConfig
        from safetensors.torch import load_file
        from pathlib import Path
        from huggingface_hub import snapshot_download
        import glob

        kwargs.get("dtype", kwargs.get("torch_dtype", None))

        # Resolve model path
        model_path = pretrained_model_name_or_path
        if not Path(model_path).exists():
            model_path = snapshot_download(pretrained_model_name_or_path)

        # Load config
        config = AutoConfig.from_pretrained(model_path)
        model = cls(
            config,
            **{
                k: v
                for k, v in kwargs.items()
                if k in ("dtype", "torch_dtype", "attn_implementation", "use_cache")
            },
        )

        # Load and remap state dict
        safetensor_files = sorted(glob.glob(str(Path(model_path) / "*.safetensors")))
        if safetensor_files:
            state_dict = {}
            for f in safetensor_files:
                state_dict.update(load_file(f))
        else:
            bin_files = sorted(glob.glob(str(Path(model_path) / "*.bin")))
            state_dict = {}
            for f in bin_files:
                state_dict.update(torch.load(f, map_location="cpu", weights_only=True))

        state_dict = _remap_keys(state_dict)
        missing, unexpected = model.load_state_dict(state_dict, strict=False)
        if missing:
            print(
                f"BiQwen3: {len(missing)} missing keys (expected for embedding-only model)"
            )
        if unexpected:
            print(f"BiQwen3: {len(unexpected)} unexpected keys: {unexpected[:5]}...")

        return model
