def test_embedding():
    """Verify BiQwen3 and swift's patched model produce the same embeddings."""
    print("\n=== Test 2: Embedding equivalence ===")

    from PIL import Image
    from transformers import AutoProcessor

    image_path = find_test_image()
    print(f"  Test image: {image_path}")

    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    processor.tokenizer.padding_side = "left"

    query = "What is the population of Tokyo?"
    image = Image.open(image_path).convert("RGB")

    # --- Contrastors path: BiQwen3 ---
    from models.biqwen3 import BiQwen3

    contrastors_model = (
        BiQwen3.from_pretrained(MODEL_NAME, dtype=torch.bfloat16).cuda().eval()
    )

    # Query embedding
    q_msgs = [
        {"role": "system", "content": [{"type": "text", "text": QUERY_INSTRUCTION}]},
        {"role": "user", "content": [{"type": "text", "text": query}]},
    ]
    q_text = processor.apply_chat_template(
        q_msgs, tokenize=False, add_generation_prompt=True
    )
    q_inputs = processor(text=[q_text], return_tensors="pt", padding="longest")
    q_inputs = {k: v.cuda() for k, v in q_inputs.items()}

    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        contrastors_q_emb = contrastors_model(**q_inputs).cpu().float()

    # Doc embedding
    d_msgs = [
        {"role": "system", "content": [{"type": "text", "text": DOC_INSTRUCTION}]},
        {"role": "user", "content": [{"type": "image"}]},
    ]
    d_text = processor.apply_chat_template(
        d_msgs, tokenize=False, add_generation_prompt=True
    )
    d_inputs = processor(
        text=[d_text], images=[image], return_tensors="pt", padding="longest"
    )
    d_inputs = {k: v.cuda() for k, v in d_inputs.items()}

    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        contrastors_d_emb = contrastors_model(**d_inputs).cpu().float()

    del contrastors_model
    torch.cuda.empty_cache()

    # --- Swift path: Qwen3VLForConditionalGeneration + patch ---
    from transformers import Qwen3VLForConditionalGeneration

    swift_model = (
        Qwen3VLForConditionalGeneration.from_pretrained(
            MODEL_NAME, torch_dtype=torch.bfloat16
        )
        .cuda()
        .eval()
    )

    # Replicate swift's embedding patch: use model.model (base Qwen3VLModel),
    # last-token pooling + L2 norm
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        # Query
        q_inputs_swift = processor(
            text=[q_text], return_tensors="pt", padding="longest"
        )
        q_inputs_swift = {k: v.cuda() for k, v in q_inputs_swift.items()}
        q_out = swift_model.model(
            **q_inputs_swift,
            use_cache=False,
            output_hidden_states=True,
            return_dict=True,
        )
        swift_q_emb = q_out.last_hidden_state[:, -1]
        swift_q_emb = (
            (swift_q_emb / swift_q_emb.norm(dim=-1, keepdim=True)).cpu().float()
        )

        # Doc
        d_inputs_swift = processor(
            text=[d_text], images=[image], return_tensors="pt", padding="longest"
        )
        d_inputs_swift = {k: v.cuda() for k, v in d_inputs_swift.items()}
        d_out = swift_model.model(
            **d_inputs_swift,
            use_cache=False,
            output_hidden_states=True,
            return_dict=True,
        )
        swift_d_emb = d_out.last_hidden_state[:, -1]
        swift_d_emb = (
            (swift_d_emb / swift_d_emb.norm(dim=-1, keepdim=True)).cpu().float()
        )

    del swift_model
    torch.cuda.empty_cache()

    # Compare
    q_cosine = torch.nn.functional.cosine_similarity(
        contrastors_q_emb, swift_q_emb
    ).item()
    d_cosine = torch.nn.functional.cosine_similarity(
        contrastors_d_emb, swift_d_emb
    ).item()
    q_maxdiff = (contrastors_q_emb - swift_q_emb).abs().max().item()
    d_maxdiff = (contrastors_d_emb - swift_d_emb).abs().max().item()

    print(f"  Query embedding:  cosine={q_cosine:.6f}  max_diff={q_maxdiff:.6e}")
    print(f"  Doc embedding:    cosine={d_cosine:.6f}  max_diff={d_maxdiff:.6e}")

    # bf16 precision: two different code paths (Qwen3VLModel vs ConditionalGeneration.model)
    # accumulate small numerical differences. 0.999 is a reasonable threshold.
    assert q_cosine > 0.999, f"Query embedding diverged: cosine={q_cosine}"
    assert d_cosine > 0.999, f"Doc embedding diverged: cosine={d_cosine}"
    print("  PASSED ✓")
    return True
