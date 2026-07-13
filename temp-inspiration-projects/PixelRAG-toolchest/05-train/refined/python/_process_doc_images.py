def _process_doc_images(processor, images):
    messages_batch = [
        [
            {"role": "system", "content": [{"type": "text", "text": DOC_INSTRUCTION}]},
            {"role": "user", "content": [{"type": "image", "image": img}]},
        ]
        for img in images
    ]
    texts = [
        processor.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
        for m in messages_batch
    ]
    return processor(text=texts, images=images, return_tensors="pt", padding="longest")
