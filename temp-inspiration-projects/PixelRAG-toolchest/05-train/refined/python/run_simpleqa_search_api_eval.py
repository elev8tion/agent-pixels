def run_simpleqa_search_api_eval(
    model,
    processor,
    examples,
    device,
    search_api_url,
    vllm_url="",
    vllm_model="",
    batch_size=32,
    n_docs=3,
    grader_model="gpt-4.1-2025-04-14",
    vllm_max_tokens=200,
    vllm_enable_thinking=False,
):
    """Run SimpleQA retrieval, compute article recall, then judge QA correctness."""
    import base64
    import io
    import re

    metrics = {}

    queries = [item["query"] for item in examples]
    query_embs = embed_query_texts(
        model, processor, queries, device, batch_size=batch_size
    )
    search_resp = search_api_by_embeddings(search_api_url, query_embs, n_docs=n_docs)

    if not vllm_url:
        logger.info("SimpleQA will use hosted OpenAI API (no --vllm-url provided)")

    # VQA answer client — uses vLLM if provided, else OpenAI
    # vLLM with multi-image VQA can take >60s per request
    answer_client = build_openai_client(vllm_url, timeout=180)
    answer_client.models.list()

    # Grader client — always uses hosted OpenAI API so we can use GPT-4.1
    grader_client = build_openai_client("", timeout=60)

    recall1 = 0
    recall3 = 0
    recall_total = 0
    correct = 0
    total = 0
    # --- Phase 1: compute recall from search results (URL-based, matching pixelrag eval) ---
    from urllib.parse import unquote

    def _norm_url(u):
        return unquote(u.strip().split("#")[0])

    def _find_wikipedia_url(urls):
        """Extract the first en.wikipedia.org URL from a list."""
        all_parts = []
        for raw in urls:
            for part in raw.split("\n"):
                part = part.strip().lstrip("- ").strip().split("#")[0]
                if "wikipedia.org/wiki/" in part:
                    all_parts.append(part)
        for part in all_parts:
            if "en.wikipedia.org/wiki/" in part:
                return part
        return (
            all_parts[0]
            if all_parts
            else (urls[0].split("#")[0].lstrip("- ").strip() if urls else None)
        )

    for example, result in zip(examples, search_resp["results"]):
        gt_url = _find_wikipedia_url(example.get("urls", []))
        if not gt_url:
            continue
        gt_url = _norm_url(gt_url)
        hit_urls = [_norm_url(hit.get("url", "")) for hit in result["hits"][:n_docs]]
        recall_total += 1
        if hit_urls and hit_urls[0] == gt_url:
            recall1 += 1
        if any(u == gt_url for u in hit_urls):
            recall3 += 1

    # --- Phase 2: VQA answers via vLLM (concurrent) ---
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def _do_vqa(idx, example, result):
        try:
            # Query text FIRST, then images (matches naive baseline order)
            content_parts = [{"type": "text", "text": example["query"]}]
            for hit in result["hits"][:n_docs]:
                img = fetch_tile_image(search_api_url, hit["path"])
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                content_parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    }
                )
            resp = answer_client.chat.completions.create(
                model=vllm_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a research assistant who answers questions based on provided evidence.\nUse <think></think> tags to show your reasoning if needed.\nAnswer the question directly and concisely based ONLY on the provided evidence.",
                    },
                    {"role": "user", "content": content_parts},
                ],
                max_tokens=vllm_max_tokens,
                temperature=0,
                **(
                    {
                        "extra_body": {
                            "chat_template_kwargs": {
                                "enable_thinking": vllm_enable_thinking
                            }
                        }
                    }
                    if "Qwen3.5" in vllm_model or vllm_enable_thinking
                    else {}
                ),
            )
            predicted = resp.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"SimpleQA [{idx + 1}] VQA failed: {e}")
            predicted = ""
        return idx, predicted

    # vLLM concurrency limited to avoid OOM on the single GPU
    vqa_concurrency = 4
    predictions = [""] * len(examples)
    logger.info(
        f"SimpleQA: sending {len(examples)} VQA requests to vLLM (concurrency={vqa_concurrency})"
    )
    with ThreadPoolExecutor(max_workers=vqa_concurrency) as pool:
        futures = [
            pool.submit(_do_vqa, i, ex, res)
            for i, (ex, res) in enumerate(zip(examples, search_resp["results"]))
        ]
        for fut in as_completed(futures):
            idx, pred = fut.result()
            predictions[idx] = pred
            if (idx + 1) % 20 == 0:
                logger.info(f"SimpleQA VQA: {idx + 1}/{len(examples)} done")
    logger.info(f"SimpleQA VQA: all {len(examples)} done")

    # --- Phase 3: grade with OpenAI (concurrent) ---
    def _do_grade(idx, example, predicted):
        try:
            grade_resp = grader_client.chat.completions.create(
                model=grader_model,
                messages=[
                    {
                        "role": "user",
                        "content": _GRADER_TEMPLATE.format(
                            question=example["query"],
                            target=example["answer"],
                            predicted_answer=predicted,
                        ),
                    }
                ],
                max_tokens=5,
                temperature=0,
            )
            grade = grade_resp.choices[0].message.content.strip()
            return idx, bool(re.search(r"A", grade))
        except Exception as e:
            logger.warning(f"SimpleQA [{idx + 1}] grading failed: {e}")
            return idx, False

    gradeable = [
        (i, ex, predictions[i]) for i, ex in enumerate(examples) if ex.get("answer")
    ]
    total = len(gradeable)
    if total > 0:
        logger.info(f"SimpleQA: grading {total} answers via OpenAI ({grader_model})")
        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = [pool.submit(_do_grade, i, ex, pred) for i, ex, pred in gradeable]
            for fut in as_completed(futures):
                idx, is_correct = fut.result()
                if is_correct:
                    correct += 1

    if total > 0:
        metrics["qa_score"] = correct / total
        metrics["qa_correct"] = correct
        metrics["qa_total"] = total
    if recall_total > 0:
        metrics["recall@1"] = recall1 / recall_total
        metrics["recall@3"] = recall3 / recall_total
        metrics["recall_total"] = recall_total
    return metrics
