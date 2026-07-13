def grade_with_gpt(results, model: str, concurrency: int = 16):
    from openai import OpenAI

    client = OpenAI()

    def _grade(idx, r):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": _GRADER_TEMPLATE.format(
                            question=r["query"],
                            target=r["golden"],
                            predicted_answer=r["predicted"] or "(no answer)",
                        ),
                    }
                ],
                max_tokens=5,
                temperature=0,
            )
            grade = resp.choices[0].message.content.strip()
            is_correct = bool(re.match(r"^\s*A\b", grade))
            return idx, is_correct, grade
        except Exception as e:
            return idx, False, f"ERR:{e}"

    scored = [(i, r) for i, r in enumerate(results) if not r.get("image_missing")]
    n = len(scored)
    verdicts = [("", False)] * len(results)
    correct = 0
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(_grade, i, r) for i, r in scored]
        for fut in tqdm(as_completed(futures), total=n, desc="GPT judge"):
            idx, is_correct, grade = fut.result()
            verdicts[idx] = (grade, is_correct)
            if is_correct:
                correct += 1

    for i, (grade, is_correct) in enumerate(verdicts):
        results[i]["judge_grade"] = grade
        results[i]["judge_correct"] = is_correct
    return {
        "llm_judge_accuracy": correct / n if n else 0.0,
        "llm_judge_correct": correct,
        "llm_judge_total": n,
    }
