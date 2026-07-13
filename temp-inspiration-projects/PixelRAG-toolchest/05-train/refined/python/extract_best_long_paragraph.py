def extract_best_long_paragraph(text: str, min_paragraph_words: int) -> str | None:
    best = None
    best_score = None
    for paragraph in split_paragraphs(text):
        normalized = normalize_text(paragraph)
        word_count = len(paragraph.split())
        sentence_count = len(re.findall(r"[.!?]", paragraph))
        if is_list_like_paragraph(paragraph):
            continue
        if word_count < min_paragraph_words:
            continue
        if sentence_count < 2:
            continue
        if "|" in paragraph:
            continue
        if normalized.startswith(
            ("references", "external links", "see also", "bibliography", "notes")
        ):
            continue
        score = (word_count, sentence_count, len(paragraph))
        if best_score is None or score > best_score:
            best = paragraph
            best_score = score
    return best
