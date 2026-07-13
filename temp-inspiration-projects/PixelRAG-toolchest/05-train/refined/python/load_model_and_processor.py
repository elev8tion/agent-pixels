def load_model_and_processor(model_name, adapter_path=None, max_visual_tokens=256):
    from models.biqwen3 import BiQwen3
    from transformers import AutoProcessor

    model = BiQwen3.from_pretrained(model_name, dtype=torch.bfloat16)
    processor = AutoProcessor.from_pretrained(model_name)
    patch_size = processor.image_processor.patch_size
    merge_size = processor.image_processor.merge_size
    tile = patch_size * merge_size
    processor.image_processor.max_pixels = max_visual_tokens * tile * tile
    processor.image_processor.size["longest_edge"] = (
        processor.image_processor.max_pixels
    )
    processor.tokenizer.padding_side = "left"

    if adapter_path:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, adapter_path)
        logger.info(f"Loaded LoRA adapter from {adapter_path}")

    model.eval()
    model.cuda()
    return model, processor
