def grade_monaco(predicted: str, validated_answer: Any) -> dict:
    """Grade a MoNaCo prediction against the validated_answer field.

    MoNaCo validated_answer is either:
      - a flat list of strings: ['ans1', 'ans2', ...]
      - a list of tuples (list of lists): [['a','b'], ['c','d']]

    For a flat list, we treat the gold as the joined string "ans1, ans2, ..."
    and compute token F1 against it.

    For list-of-tuples, we compute max F1 over all tuple-combinations.

    Returns dict with 'em' and 'f1'.
    """
    if not validated_answer:
        return {"em": 0, "f1": 0.0}

    # Flatten gold answer to a single string for token F1
    if isinstance(validated_answer, list):
        if all(isinstance(x, list) for x in validated_answer):
            # List of tuples: compute max F1 over all combinations
            # (each combination is one element from each tuple)
            # But for simplicity, flatten all elements as gold tokens
            flat = []
            for sub in validated_answer:
                flat.extend(sub)
            gold_str = ", ".join(str(a) for a in flat)
        else:
            gold_str = ", ".join(str(a) for a in validated_answer)
    else:
        gold_str = str(validated_answer)

    f1 = token_f1(predicted, gold_str)
    em = exact_match(predicted, gold_str)
    return {"em": em, "f1": f1}
