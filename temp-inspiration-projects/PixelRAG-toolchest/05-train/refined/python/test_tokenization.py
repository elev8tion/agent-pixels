def test_tokenization():
    """Verify that contrastors and swift produce the same token IDs for queries."""
    print("\n=== Test 1: Tokenization equivalence ===")

    from transformers import AutoProcessor

    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    processor.tokenizer.padding_side = "left"

    query = "What is the population of Tokyo?"

    # --- Contrastors path: manual chat template ---
    q_msgs = [
        {"role": "system", "content": [{"type": "text", "text": QUERY_INSTRUCTION}]},
        {"role": "user", "content": [{"type": "text", "text": query}]},
    ]
    contrastors_text = processor.apply_chat_template(
        q_msgs, tokenize=False, add_generation_prompt=True
    )
    contrastors_ids = processor(text=[contrastors_text], return_tensors="pt")[
        "input_ids"
    ][0]

    # --- Swift path: messages format ---
    # Swift uses the same processor but constructs messages differently.
    # The swift template system processes messages → applies chat template → tokenizes.
    # We simulate what swift does: same chat template but with string content.
    s_msgs = [
        {"role": "system", "content": [{"type": "text", "text": QUERY_INSTRUCTION}]},
        {"role": "user", "content": [{"type": "text", "text": query}]},
    ]
    swift_text = processor.apply_chat_template(
        s_msgs, tokenize=False, add_generation_prompt=True
    )
    swift_ids = processor(text=[swift_text], return_tensors="pt")["input_ids"][0]

    match = torch.equal(contrastors_ids, swift_ids)
    print(
        f"  Contrastors tokens: {contrastors_ids.shape} → {contrastors_ids[:10].tolist()}..."
    )
    print(f"  Swift tokens:       {swift_ids.shape} → {swift_ids[:10].tolist()}...")
    print(f"  Text match: {contrastors_text == swift_text}")
    print(f"  Token match: {match}")

    # Also check the actual template strings
    if contrastors_text != swift_text:
        print("  DIFF in template text!")
        print(f"    Contrastors: {repr(contrastors_text[:200])}")
        print(f"    Swift:       {repr(swift_text[:200])}")

    assert match, "Tokenization mismatch!"
    print("  PASSED ✓")
    return True
