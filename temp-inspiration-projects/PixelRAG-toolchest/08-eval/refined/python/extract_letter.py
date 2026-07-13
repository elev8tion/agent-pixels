def extract_letter(response: str) -> str:
    """Extract A-E letter from model response."""
    response = response.strip()
    if response and response[0] in LETTERS:
        return response[0]
    for ch in LETTERS:
        if ch in response:
            return ch
    return response[:1] if response else ""
