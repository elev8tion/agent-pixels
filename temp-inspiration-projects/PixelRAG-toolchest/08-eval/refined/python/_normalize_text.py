def _normalize_text(s: str) -> str:
    s = re.sub(
        r"\b(a|an|the)\b",
        " ",
        s.lower().translate(str.maketrans("", "", string.punctuation)),
    )
    return " ".join(s.split())
