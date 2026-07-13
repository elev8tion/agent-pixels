def process_doc_images(processor, images):
    """Wrap document images in chat template with representation instruction.

    Returns batch-major pixel_values (B, max_patches, dim) so that
    chunk_inputs / GradCache can split along the batch dimension.
    BiQwen3.forward() un-pads back to flat before passing to Qwen3VLModel.
    """
    texts = [_DOC_IMAGE_TMPL] * len(images)
    batch = processor(text=texts, images=images, return_tensors="pt", padding="longest")

    # Reshape pixel_values from flat (total_patches, dim) to batch-major
    # (B, max_patches, dim) for GradCache chunking compatibility.
    if "pixel_values" in batch and "image_grid_thw" in batch:
        offsets = batch["image_grid_thw"].prod(dim=1).tolist()
        pixel_chunks = list(torch.split(batch["pixel_values"], offsets))
        batch["pixel_values"] = torch.nn.utils.rnn.pad_sequence(
            pixel_chunks, batch_first=True
        )

    return batch
