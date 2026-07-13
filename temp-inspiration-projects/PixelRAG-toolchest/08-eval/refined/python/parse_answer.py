def parse_answer(reply: str) -> str:
    """Extract the final answer from agent output."""
    if not reply:
        return ""
    matches = _ANSWERS_PAT.findall(reply)
    if matches:
        return matches[-1].strip().rstrip(".")
    return reply.splitlines()[-1].strip() if reply else ""
