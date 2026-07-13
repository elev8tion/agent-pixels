def _process_queries(processor, queries):
    messages_batch = [
        [
            {
                "role": "system",
                "content": [{"type": "text", "text": QUERY_INSTRUCTION}],
            },
            {"role": "user", "content": [{"type": "text", "text": q}]},
        ]
        for q in queries
    ]
    texts = [
        processor.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
        for m in messages_batch
    ]
    return processor(text=texts, return_tensors="pt", padding="longest")
