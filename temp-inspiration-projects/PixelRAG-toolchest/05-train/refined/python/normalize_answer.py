def normalize_answer(answer: str) -> str:
    return answer.strip().upper().replace('"', "").replace("`", "")
