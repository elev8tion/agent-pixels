def format_assistant(reasoning: str, answer: str) -> str:
    # Qwen3 thinking format: <think>...</think>answer
    return f"<think>\n{reasoning.strip()}\n</think>\n\n{answer.strip()}"
