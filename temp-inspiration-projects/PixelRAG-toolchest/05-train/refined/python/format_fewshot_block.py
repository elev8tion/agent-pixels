def format_fewshot_block(examples: list[dict]) -> str:
    blocks = []
    for idx, ex in enumerate(examples, 1):
        blocks.append(
            f"""Example {idx}
Passage:
\"\"\"
{ex["text"]}
\"\"\"
Good output:
Q: {ex["question"]}
A: {ex["answer"]}
S: {ex["supporting_span"]}
T: prose"""
        )
    return "\n\n".join(blocks)
