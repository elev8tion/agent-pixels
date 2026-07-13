def _build_chat_prompt(tokenizer, instruction: str | None = None) -> str:
    """Build the embedding prompt using the model's chat template.

    Uses the official Qwen3-VL-Embedding prompt format:
        system: <instruction>
        user: [image]
    """
    instr = instruction if instruction is not None else _INSTRUCTION
    conversation = [
        {"role": "system", "content": [{"type": "text", "text": instr}]},
        {"role": "user", "content": [{"type": "image"}]},
    ]
    return tokenizer.apply_chat_template(
        conversation,
        tokenize=False,
        add_generation_prompt=True,
    )
