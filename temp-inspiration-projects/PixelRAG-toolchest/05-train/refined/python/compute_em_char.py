def compute_em_char(results):
    correct_em = 0
    char_correct = 0
    char_total = 0
    scored = 0
    for r in results:
        if r.get("image_missing"):
            continue
        scored += 1
        pred = r["predicted"].lower()
        gold = r["golden"].lower()
        if pred == gold:
            correct_em += 1
        if gold or pred:
            matches = sum(1 for a, b in zip(pred, gold) if a == b)
            char_correct += matches
            char_total += max(len(pred), len(gold))
    return {
        "exact_match": correct_em / scored if scored else 0.0,
        "char_accuracy": char_correct / char_total if char_total else 0.0,
        "scored": scored,
    }
