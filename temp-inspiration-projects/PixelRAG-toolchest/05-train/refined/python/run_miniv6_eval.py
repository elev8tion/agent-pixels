@torch.no_grad()
def run_miniv6_eval(
    model,
    processor,
    test_data,
    device,
    batch_size=64,
    vllm_url="",
    vllm_model="",
    grader_model="gpt-4.1-2025-04-14",
    output_path=None,
    vllm_max_tokens=200,
    vllm_enable_thinking=False,
):
    """Evaluate on mini-v6 tiles: R@1, R@3, and optional QA score via vLLM.

    Args:
        output_path: If set, save per-example results as JSONL.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import re

    raw = model.module if hasattr(model, "module") else model
    raw.eval()

    questions = test_data["questions"]
    doc_paths = test_data["doc_paths"]
    golden_mapping = test_data["golden_mapping"]

    def _load_image(path):
        with Image.open(path) as im:
            return im.convert("RGB")

    # Embed queries
    t_eval_start = time.time()
    query_texts = [q["problem"] for q in questions]
    q_embs = []
    for i in range(0, len(query_texts), batch_size * 2):
        batch = query_texts[i : i + batch_size * 2]
        inputs = process_queries(processor, batch)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.autocast("cuda", dtype=torch.bfloat16):
            _clear_rope_deltas(raw)
            _bidir = getattr(raw, "_bidirectional", False)
            emb = raw(**inputs, bidirectional=_bidir)
        q_embs.append(emb.cpu().float().numpy())
    t_query_emb = time.time()
    logger.info(
        f"  [profile] query embed: {t_query_emb - t_eval_start:.1f}s ({len(query_texts)} queries)"
    )

    # Embed images — use cached preprocessed tensors if available
    max_px = processor.image_processor.max_pixels
    cache_path = os.path.join(
        os.path.dirname(doc_paths[0]),
        f".tile_cache_n{len(doc_paths)}_px{max_px}_bs{batch_size}.pt",
    )

    i_embs = []
    if os.path.exists(cache_path):
        # Fast path: load preprocessed batches from cache
        cached_batches = torch.load(cache_path, map_location="cpu", weights_only=True)
        logger.info(
            f"  [cache] loaded {len(cached_batches)} preprocessed tile batches from {cache_path}"
        )
        for inputs in cached_batches:
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.autocast("cuda", dtype=torch.bfloat16):
                _clear_rope_deltas(raw)
                emb = raw(**inputs, bidirectional=_bidir)
            i_embs.append(emb.cpu().float().numpy())
    else:
        # Slow path: preprocess from images, then save cache
        cached_batches = []
        pool = ThreadPoolExecutor(max_workers=4)
        batched_paths = [
            doc_paths[i : i + batch_size] for i in range(0, len(doc_paths), batch_size)
        ]
        future = (
            pool.submit(
                lambda paths: list(pool.map(_load_image, paths)), batched_paths[0]
            )
            if batched_paths
            else None
        )
        for idx, _ in enumerate(batched_paths):
            images = future.result()
            if idx + 1 < len(batched_paths):
                next_paths = batched_paths[idx + 1]
                future = pool.submit(
                    lambda paths: list(pool.map(_load_image, paths)), next_paths
                )
            inputs = process_doc_images(processor, images)
            # Save CPU tensors for cache
            cached_batches.append({k: v.cpu() for k, v in inputs.items()})
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.autocast("cuda", dtype=torch.bfloat16):
                _clear_rope_deltas(raw)
                emb = raw(**inputs, bidirectional=_bidir)
            i_embs.append(emb.cpu().float().numpy())
            for img in images:
                img.close()
        pool.shutdown(wait=False)
        # Save cache for future evals
        try:
            torch.save(cached_batches, cache_path)
            logger.info(
                f"  [cache] saved {len(cached_batches)} preprocessed tile batches to {cache_path}"
            )
        except Exception as e:
            logger.warning(f"  [cache] failed to save: {e}")

    t_doc_emb = time.time()
    logger.info(
        f"  [profile] doc embed: {t_doc_emb - t_query_emb:.1f}s ({len(doc_paths)} tiles)"
    )

    q_embs = np.concatenate(q_embs, axis=0)
    i_embs = np.concatenate(i_embs, axis=0)

    # Compute R@1, R@3 using article-level matching + collect top-3 paths per query
    sims = q_embs @ i_embs.T  # (Q, D)
    r1 = r3 = has_golden = 0
    top3_per_query = []
    per_example_results = []
    for qi, q in enumerate(questions):
        top_idx = np.argsort(sims[qi])[::-1][:3]
        top3_paths = [doc_paths[i] for i in top_idx]
        top3_per_query.append(top3_paths)
        gids = golden_mapping.get(q["id"], [])
        rids = [
            os.path.basename(p).replace("dist_", "").split("_chunk_")[0]
            for p in top3_paths
        ]
        hit1 = bool(gids and rids[0] in gids)
        hit3 = bool(gids and any(rid in gids for rid in rids))
        if gids:
            has_golden += 1
            if hit1:
                r1 += 1
            if hit3:
                r3 += 1
        per_example_results.append(
            {
                "id": q["id"],
                "problem": q["problem"],
                "answer": q.get("answer", ""),
                "top3_paths": top3_paths,
                "top3_article_ids": rids,
                "golden_ids": gids,
                "hit@1": hit1,
                "hit@3": hit3,
            }
        )

    t_ranking = time.time()
    logger.info(f"  [profile] ranking: {t_ranking - t_doc_emb:.1f}s")

    metrics = {
        "recall@1": r1 / has_golden if has_golden else 0,
        "recall@3": r3 / has_golden if has_golden else 0,
    }

    # QA scoring: VQA via vLLM, grading via OpenAI (GPT-4.1)
    if vllm_url:
        try:
            import base64

            os.environ.get("VLLM_API_KEY", "dummy")
            answer_client = build_openai_client(vllm_url, timeout=180)
            grader_client = build_openai_client("", timeout=60)

            def _do_qa(qi):
                q = questions[qi]
                answer = q.get("answer", "")
                if not answer:
                    return qi, "", "", False
                # Query text FIRST, then images
                content_parts = [{"type": "text", "text": q["problem"]}]
                for p in top3_per_query[qi]:
                    with open(p, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()
                    content_parts.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"},
                        }
                    )
                try:
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
                except Exception:
                    predicted = ""
                # Grade with OpenAI GPT-4.1
                is_correct = False
                try:
                    grade_resp = grader_client.chat.completions.create(
                        model=grader_model,
                        messages=[
                            {
                                "role": "user",
                                "content": _GRADER_TEMPLATE.format(
                                    question=q["problem"],
                                    target=answer,
                                    predicted_answer=predicted,
                                ),
                            }
                        ],
                        max_tokens=5,
                        temperature=0,
                    )
                    grade = grade_resp.choices[0].message.content.strip()
                    if re.search(r"A", grade):
                        is_correct = True
                except Exception:
                    grade = ""
                return qi, predicted, grade, is_correct

            correct = total = 0
            with ThreadPoolExecutor(max_workers=4) as qa_pool:
                futures = [
                    qa_pool.submit(_do_qa, qi)
                    for qi in range(len(questions))
                    if questions[qi].get("answer")
                ]
                for fut in as_completed(futures):
                    qi, predicted, grade, is_correct = fut.result()
                    per_example_results[qi]["predicted"] = predicted
                    per_example_results[qi]["grade"] = grade
                    per_example_results[qi]["correct"] = is_correct
                    if is_correct:
                        correct += 1
                    total += 1

            if total > 0:
                metrics["qa_score"] = correct / total
                t_qa = time.time()
                logger.info(
                    f"  QA: {correct}/{total} = {correct / total:.3f} "
                    f"[profile: {t_qa - t_ranking:.1f}s]"
                )
        except Exception as e:
            logger.warning(f"QA eval failed: {e}")

    # Save per-example results
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            for item in per_example_results:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        logger.info(f"  Saved {len(per_example_results)} eval results to {output_path}")

    logger.info(f"  [profile] eval total: {time.time() - t_eval_start:.1f}s")
    raw.train()
    return metrics
