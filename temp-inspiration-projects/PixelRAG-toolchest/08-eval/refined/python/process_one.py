def process_one(
    ex: dict, model: str, retrieval: str, api_key: str, base_url: str
) -> dict:
    """Run the ReAct agent on one MoNaCo example. Returns prediction record."""
    t0 = time.time()
    ex_num = ex["ex_num"]
    question = ex["question"]
    decomp = ex.get("decomposition") or []

    try:
        result = react_loop(question, model, retrieval, api_key, base_url)
        final_answer = parse_answer(result["final"])
        output = (
            f"Let's think step by step:\n"
            f"[self-decomp ReAct, {result['turns']} turns, {result['searches']} searches]\n"
            f"\nAnswers: {final_answer}"
        )
        rec: dict = {
            "question": question,
            "output": output,
            "qa_type": f"agent_self_decomp_{retrieval}",
            "llm": model,
            "gold_decomposition": "\n".join(
                f"{i + 1}. {s}" for i, s in enumerate(decomp)
            ),
            "ex_num": ex_num,
            "gold_question": question,
            "elapsed_sec": round(time.time() - t0, 2),
            "n_turns": result["turns"],
            "n_searches": result["searches"],
            "k_values": result["k_values"],
            "trace": result["trace"],
        }
    except Exception as e:
        rec = {
            "question": question,
            "output": "Let's think step by step: [agent_error]\nAnswers: [error]",
            "qa_type": f"agent_self_decomp_{retrieval}",
            "llm": model,
            "gold_decomposition": "\n".join(
                f"{i + 1}. {s}" for i, s in enumerate(decomp)
            ),
            "ex_num": ex_num,
            "gold_question": question,
            "elapsed_sec": round(time.time() - t0, 2),
            "n_turns": 0,
            "n_searches": 0,
            "k_values": [],
            "trace": [],
            "agent_error": str(e),
            "agent_traceback": traceback.format_exc(),
        }

    # Inline F1 grading if gold answer is available
    validated_answer = ex.get("validated_answer")
    if validated_answer is not None:
        predicted = parse_answer(rec.get("output", ""))
        scores = grade_monaco(predicted, validated_answer)
        rec["token_f1"] = scores["f1"]
        rec["token_em"] = scores["em"]
        rec["gold_answers"] = validated_answer

    return rec
