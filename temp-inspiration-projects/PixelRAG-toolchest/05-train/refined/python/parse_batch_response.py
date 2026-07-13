def parse_batch_response(text: str, n: int) -> list[bool]:
    results = [True] * n
    if not text:
        return results
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(\d+)[:.)\s]+(?:N:\s*)?(YES|NO)", line, re.IGNORECASE)
        if m:
            idx = int(m.group(1)) - 1
            verdict = m.group(2).upper()
            if 0 <= idx < n:
                results[idx] = verdict == "YES"
    return results
