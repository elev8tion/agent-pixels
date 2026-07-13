def _gold_length(validated_answer: Any) -> int:
    """MoNaCo gold_answers_length convention."""
    if not isinstance(validated_answer, list) or not validated_answer:
        return 0
    if all(isinstance(x, list) for x in validated_answer):
        return sum(len(x) for x in validated_answer)
    return len(validated_answer)
