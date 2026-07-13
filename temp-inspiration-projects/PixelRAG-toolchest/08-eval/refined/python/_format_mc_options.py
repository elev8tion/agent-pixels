def _format_mc_options(labels: list[str], texts: list[str]) -> str:
    """Format MC options as 'A. text1\nB. text2\n...'"""
    return "\n".join(f"{label}. {text}" for label, text in zip(labels, texts))
