async def grade_file(
    task: str,
    path: str,
    grader_model: str = DEFAULT_GRADER_MODEL,
    concurrency: int = 16,
) -> dict:
    if task in EXACT_MATCH_TASKS:
        return grade_exact_match(path)
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"], base_url=os.environ.get("OPENAI_BASE_URL")
    )
    rows = [json.loads(l) for l in open(path)]
    sem = asyncio.Semaphore(concurrency)
    labels = [None] * len(rows)

    is_sqa = task in SIMPLEQA_TASKS

    async def judge(i, d):
        od = d.get("original_data", {})
        answer = strip_think(d.get("final_response"))
        if is_sqa:
            target = od.get("answer", "") or od.get("gt_answer", "")
            prompt = SIMPLEQA_GRADER_TEMPLATE.format(
                question=d.get("problem", ""), target=target, predicted_answer=answer
            )
        else:
            gt = build_ground_truth(task, od)
            prompt = JUDGE_WORLDQA_PROMPT_EN.format(
                question=d.get("problem", ""),
                model_answer=answer,
                ground_truth_answer=gt,
            )
        async with sem:
            try:
                r = await client.chat.completions.create(
                    model=grader_model,
                    temperature=0,
                    max_tokens=GRADER_MAX_TOKENS,
                    seed=GRADER_SEED,
                    messages=[
                        {"role": "system", "content": GRADER_SYSTEM_MESSAGE},
                        {"role": "user", "content": prompt},
                    ],
                )
                out = r.choices[0].message.content
                if is_sqa:
                    m = re.search(r"(A|B|C)", out or "")
                    letter = m.group(0) if m else "C"
                    labels[i] = {"A": "correct", "B": "incorrect", "C": "unattempted"}[
                        letter
                    ]
                else:
                    labels[i] = parse_label(out)
            except Exception as e:
                labels[i] = ("__error__", str(e))

    await asyncio.gather(*[judge(i, d) for i, d in enumerate(rows)])
    errs = [l for l in labels if isinstance(l, tuple)]
    verdicts = [l for l in labels if isinstance(l, str)]
    n = len(verdicts)
    c = verdicts.count("correct")
    inc = verdicts.count("incorrect")
    una = verdicts.count("unattempted")
    return {
        "task": task,
        "file": path,
        "n": n,
        "correct": c,
        "incorrect": inc,
        "unattempted": una,
        "errors": len(errs),
        "score": c / n if n else 0.0,
    }
