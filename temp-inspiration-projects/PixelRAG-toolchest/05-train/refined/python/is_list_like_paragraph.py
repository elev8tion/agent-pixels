def is_list_like_paragraph(paragraph: str) -> bool:
    lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
    if not lines:
        return True
    bulletish = 0
    pipe_lines = 0
    short_lines = 0
    for line in lines:
        if line.startswith(("-", "*", "|")):
            bulletish += 1
        if "|" in line:
            pipe_lines += 1
        if len(line.split()) <= 6:
            short_lines += 1
    if bulletish >= max(2, len(lines) // 2):
        return True
    if pipe_lines >= max(2, len(lines) // 2):
        return True
    if short_lines >= max(3, len(lines) // 2 + 1):
        return True
    return False
