def get_output_filename(
    output_dir: str,
    model_name: str,
    mode: str = "naive",
    num_examples: int = 1000,
    url_screenshot: bool = False,
    task: str = "simpleqa",
) -> str:
    """
    Generate output filename with model name and task included.

    Args:
        output_dir: Base output directory (e.g., 'eval_output/naive_qa')
        model_name: Model name (e.g., 'Qwen/Qwen3-VL-4B-Instruct')
        mode: Evaluation mode ('naive', 'screenshot', 'retrieval')
        num_examples: Number of examples
        url_screenshot: Whether URL screenshot mode is enabled
        task: Task/benchmark name (e.g., 'simpleqa', 'encyclopedic_vqa', 'worldvqa')

    Returns:
        Full output file path
    """
    # Clean model name for filename (replace special chars)
    model_safe = (
        model_name.replace("/", "_").replace(":", "_").replace("-", "_").lower()
    )

    # Build filename components (task first for easy distinction)
    parts = [task]
    if url_screenshot:
        parts.append("urlscreenshot")
    parts.append(mode)
    parts.append(model_safe)
    parts.append(str(num_examples))

    filename = "_".join(parts) + ".jsonl"
    return os.path.join(output_dir, filename)
