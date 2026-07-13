def strip_think(text: str) -> str:
    # Verbatim from paper worldvqa_eval.strip_think_tags.
    if text is None:
        return ""
    if "<think>" in text and "</think>" in text:
        return text.split("</think>")[-1].strip()
    elif "think>" in text:
        return text.split("think>")[-1].strip()
    return text
