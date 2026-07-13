def is_candidate_passage(text: str, n_tokens: int) -> bool:
    if not text or len(text.strip()) < 300:
        return False
    if n_tokens < 80:
        return False
    title = infer_title(text)
    if is_bad_title(title):
        return False
    prefix = normalize_text(text[:400])
    if "may refer to:" in prefix:
        return False
    return True
