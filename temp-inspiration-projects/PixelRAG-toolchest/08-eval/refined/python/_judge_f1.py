def _judge_f1(predicted_num: int, correct_preds: list[str], gold_len: int) -> dict:
    num_correct = 0 if correct_preds == ["NULL"] else len(correct_preds)
    p = num_correct / predicted_num if predicted_num > 0 else 0.0
    r = num_correct / gold_len if gold_len > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return {
        "judge_f1": f1,
        "judge_p": p,
        "judge_r": r,
        "judge_n_correct": num_correct,
        "judge_n_pred": predicted_num,
        "judge_gold_len": gold_len,
    }
