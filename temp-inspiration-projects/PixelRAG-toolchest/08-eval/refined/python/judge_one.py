def judge_one(rec: dict, judge_model: str, api_key: str, base_url: str) -> dict:
    """Run the MoNaCo LLM judge on one prediction record. Returns judge scores."""
    validated_answer = rec.get("gold_answers")
    if validated_answer is None:
        return {}
    question = rec["question"]
    response = rec.get("output", "")
    prompt = JUDGE_PROMPT.format(
        question=question,
        response=response,
        correct_answer=str(validated_answer),
    )
    body = {
        "model": judge_model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
        "temperature": 0.0,
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    last_exc = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                d = json.load(resp)
            judgement = d["choices"][0]["message"].get("content", "") or ""
            n_pred, correct_preds = _parse_judge_response(judgement)
            gl = _gold_length(validated_answer)
            scores = _judge_f1(n_pred, correct_preds, gl)
            scores["judge_raw"] = judgement[:2000]
            return scores
        except urllib.error.HTTPError as e:
            last_exc = e
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(min(60, 2**attempt + 2))
                continue
            raise
        except urllib.error.URLError as e:
            last_exc = e
            if attempt < 3:
                time.sleep(min(60, 2**attempt + 2))
                continue
            raise
    raise last_exc  # type: ignore[misc]
