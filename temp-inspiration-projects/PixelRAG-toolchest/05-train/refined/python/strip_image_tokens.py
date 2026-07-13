def strip_image_tokens(s: str) -> str:
    return s.replace("<image>", "").lstrip("\n ")
