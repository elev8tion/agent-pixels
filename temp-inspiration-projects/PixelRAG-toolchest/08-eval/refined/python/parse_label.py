def parse_label(judge_text: str) -> str:
    m = re.search(
        r"Label:\s*(Correct|Incorrect|Unattempted)", judge_text, re.IGNORECASE
    )
    if m:
        return m.group(1).lower()
    tl = judge_text.lower()
    if "incorrect" in tl:
        return "incorrect"
    if "unattempted" in tl:
        return "unattempted"
    if "correct" in tl:
        return "correct"
    return "incorrect"
