def run_inference(
    model, processor, examples, device, desc, max_new_tokens=128, enable_thinking=False
):
    results = []
    for ex in tqdm(examples, desc=desc):
        images = ex.get("images", [])
        # Verify all images exist
        missing = [p for p in images if not os.path.exists(p)]
        if missing:
            results.append(
                {
                    "query": ex.get("_query", ""),
                    "golden": ex.get("_golden", ""),
                    "predicted": "",
                    "image_missing": True,
                    "missing_paths": missing,
                }
            )
            continue

        user_msg = next(m for m in ex["messages"] if m["role"] == "user")
        assistant_msg = next(m for m in ex["messages"] if m["role"] == "assistant")
        query = strip_image_tokens(user_msg["content"])
        golden = assistant_msg["content"].strip()

        content = [{"type": "image", "image": f"file://{p}"} for p in images]
        content.append({"type": "text", "text": query})
        messages = [{"role": "user", "content": content}]

        text = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=enable_thinking,
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to(device)

        with torch.no_grad():
            out_ids = model.generate(
                **inputs, max_new_tokens=max_new_tokens, do_sample=False
            )
        gen_ids = out_ids[0][inputs.input_ids.shape[1] :]
        pred = processor.decode(gen_ids, skip_special_tokens=True).strip()

        results.append(
            {
                "query": query,
                "golden": golden,
                "predicted": pred,
                "n_images": len(images),
                "gold_pos": ex.get("_gold_pos"),
                "gold_in_top6_pos": ex.get("_gold_in_top6_pos"),
            }
        )
    return results
