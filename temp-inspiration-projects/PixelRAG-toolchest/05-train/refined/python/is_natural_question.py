def is_natural_question(qa: dict, passage: str) -> bool:
    q = qa.get("query", "")
    a = qa.get("answer", "")
    s = qa.get("source_sentence", "") or ""
    src_type = qa.get("source_type", "prose")

    if src_type != "prose":
        return False
    for pat in BAD_Q_RE:
        if pat.search(q):
            return False
    if a and a[-1] in ("→", "…", "–", "/", "(", ","):
        return False
    if not s:
        return False
    if s.rstrip()[-1:] in ("(", ",", "–", "/", "→", "…"):
        return False
    if len(s.split()) < 10:
        return False
    if normalize_text(s) not in normalize_text(passage):
        return False
    return True
