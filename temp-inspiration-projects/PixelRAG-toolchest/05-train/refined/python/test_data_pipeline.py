def test_data_pipeline():
    """Verify that the full data pipeline (load image → process → embed) is equivalent.

    Loads real data samples, processes through both pipelines' collation,
    and compares the resulting token IDs and pixel values.
    """
    print("\n=== Test 6: Data pipeline (collate) equivalence ===")

    from PIL import Image
    from transformers import AutoProcessor

    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    processor.tokenizer.padding_side = "left"

    # Load 2 real samples with hard negatives
    with open("data/train_hn.jsonl") as f:
        samples = [json.loads(f.readline()) for _ in range(2)]

    # --- Contrastors collate path ---
    from train_contrastors import (
        init_chat_templates,
        process_queries,
        process_doc_images,
    )

    init_chat_templates(processor)

    queries = [s["query"] for s in samples]
    doc_images = []
    for s in samples:
        doc_images.append(Image.open(s["chunk_path"]).convert("RGB"))
        # Add first hard negative
        if s.get("neg_chunk_paths") and os.path.exists(s["neg_chunk_paths"][0]):
            doc_images.append(Image.open(s["neg_chunk_paths"][0]).convert("RGB"))

    contrastors_q = process_queries(processor, queries)
    contrastors_d = process_doc_images(processor, doc_images)

    # --- Swift path: same processor, same template ---
    # Swift ultimately calls the same processor.apply_chat_template → processor()
    # We verify the query token IDs match
    swift_q_texts = []
    for q in queries:
        msgs = [
            {
                "role": "system",
                "content": [{"type": "text", "text": QUERY_INSTRUCTION}],
            },
            {"role": "user", "content": [{"type": "text", "text": q}]},
        ]
        swift_q_texts.append(
            processor.apply_chat_template(
                msgs, tokenize=False, add_generation_prompt=True
            )
        )
    swift_q = processor(text=swift_q_texts, return_tensors="pt", padding="longest")

    # Doc images: same images, same template
    swift_d_texts = []
    for _ in doc_images:
        msgs = [
            {"role": "system", "content": [{"type": "text", "text": DOC_INSTRUCTION}]},
            {"role": "user", "content": [{"type": "image"}]},
        ]
        swift_d_texts.append(
            processor.apply_chat_template(
                msgs, tokenize=False, add_generation_prompt=True
            )
        )
    swift_d = processor(
        text=swift_d_texts, images=doc_images, return_tensors="pt", padding="longest"
    )

    # Compare query tokens
    q_match = torch.equal(contrastors_q["input_ids"], swift_q["input_ids"])
    q_attn_match = torch.equal(
        contrastors_q["attention_mask"], swift_q["attention_mask"]
    )
    print(f"  Query input_ids match:      {q_match}")
    print(f"  Query attention_mask match: {q_attn_match}")

    # Compare doc tokens
    d_ids_match = torch.equal(contrastors_d["input_ids"], swift_d["input_ids"])
    d_attn_match = torch.equal(
        contrastors_d["attention_mask"], swift_d["attention_mask"]
    )
    print(f"  Doc input_ids match:        {d_ids_match}")
    print(f"  Doc attention_mask match:   {d_attn_match}")

    # Compare pixel values — contrastors reshapes to (B, max_patches, dim),
    # swift keeps flat (total_patches, dim). Compare the flat versions.
    if "pixel_values" in contrastors_d and "pixel_values" in swift_d:
        c_pv = contrastors_d["pixel_values"]
        s_pv = swift_d["pixel_values"]
        # Contrastors: (B, max_patches, dim) → flatten valid patches
        c_offsets = contrastors_d["image_grid_thw"].prod(dim=1).tolist()
        c_flat = torch.cat(
            [c_pv[i, : c_offsets[i]] for i in range(len(c_offsets))], dim=0
        )
        # Swift: already flat (total_patches, dim)
        s_flat = (
            s_pv
            if s_pv.dim() == 2
            else torch.cat(
                [s_pv[i, : c_offsets[i]] for i in range(len(c_offsets))], dim=0
            )
        )
        pv_match = torch.equal(c_flat, s_flat)
        pv_maxdiff = (
            (c_flat.float() - s_flat.float()).abs().max().item()
            if not pv_match
            else 0.0
        )
        print(f"  Pixel values match:         {pv_match} (max_diff={pv_maxdiff:.6e})")
    else:
        pv_match = True
        print("  Pixel values: skipped (not present)")

    for img in doc_images:
        img.close()

    assert q_match, "Query input_ids mismatch!"
    assert d_ids_match, "Doc input_ids mismatch!"
    assert pv_match, "Pixel values mismatch!"
    print("  PASSED ✓")
    return True
