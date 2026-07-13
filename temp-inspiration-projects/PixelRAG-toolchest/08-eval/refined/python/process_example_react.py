async def process_example_react(
    llm_client: LLMClient,
    retriever,
    example: dict,
    semaphore: asyncio.Semaphore,
    output_file: str | None = None,
    progress_counter: dict | None = None,
    total_examples: int = 0,
    encode_image_fn=None,
    task_name: str = "simpleqa",
    tiles_dir: str | None = None,
    max_turns: int = 3,
    api_url: str = "http://localhost:30888/search",
    react_top_k: int = 5,
    nprobe: int | None = None,
    prompt_version: str = "v1",
) -> dict | None:
    """Process a single example with ReAct multi-turn retrieval.

    Flow: retrieve → LLM → if <search>query</search> in response → retrieve again → LLM → ...
    Stops when: (1) no <search> tag in response, (2) max_turns reached, or (3) error.
    """
    async with semaphore:
        try:
            example_id = example.get("id", "unknown")
            total_start = time.time()

            # Round 1: use the normal retriever (which may have prefetched results)
            retrieval_start = time.time()
            retrieval_result = await retriever.retrieve(example["problem"], example)
            retrieval_time = time.time() - retrieval_start

            retrieval_results = [retrieval_result]
            assistant_responses = []
            all_search_queries = []
            total_retrieval_time = retrieval_time
            total_llm_time = 0.0
            turns_used = 1

            _encode_fn = (
                encode_image_fn if encode_image_fn is not None else encode_screenshot
            )

            for turn in range(max_turns):
                is_last = turn == max_turns - 1
                # Build messages (multi-turn)
                messages = build_react_messages(
                    query=example["problem"],
                    retrieval_results=retrieval_results,
                    assistant_responses=assistant_responses,
                    encode_image_fn=_encode_fn,
                    prompt_version=prompt_version,
                    is_last_turn=is_last,
                    previous_queries=all_search_queries,
                )

                # Call LLM
                llm_start = time.time()
                generated_text, usage = await llm_client.generate(messages)
                total_llm_time += time.time() - llm_start

                # Check for <search> tag
                match = _SEARCH_TAG_RE.search(generated_text)
                if not match or is_last:
                    # Final answer (or last turn forced)
                    # Strip any remaining <search> tags from forced-stop responses
                    final_response = _SEARCH_TAG_RE.sub("", generated_text).strip()
                    turns_used = turn + 1
                    break

                # Extract search query and do another round
                search_query = match.group(1).strip()
                all_search_queries.append(search_query)
                assistant_responses.append(generated_text)
                logger.info(
                    f"ReAct [{example_id}] turn {turn + 1}: searching '{search_query[:80]}'"
                )

                # New retrieval
                ret_start = time.time()
                new_hits = await _local_api_search(
                    api_url, search_query, react_top_k, nprobe
                )
                total_retrieval_time += time.time() - ret_start
                retrieval_results.append(_hits_to_retrieval_result(new_hits))
            else:
                final_response = generated_text
                turns_used = max_turns

            # Update progress counter
            if progress_counter is not None:
                progress_counter["completed"] += 1
                if "retrieval_times" not in progress_counter:
                    progress_counter["retrieval_times"] = []
                    progress_counter["llm_times"] = []
                progress_counter["retrieval_times"].append(total_retrieval_time)
                progress_counter["llm_times"].append(total_llm_time)

            total_time = time.time() - total_start

            # Build per-turn traces (images + assistant response for each round)
            react_trace = []
            for turn_idx, rr in enumerate(retrieval_results):
                turn_info = {
                    "turn": turn_idx + 1,
                    "images": [
                        {"path": path, "score": score, "url": rr.source_url}
                        for path, score in rr.images
                    ],
                }
                if turn_idx < len(assistant_responses):
                    turn_info["assistant_response"] = assistant_responses[turn_idx]
                elif turn_idx == len(retrieval_results) - 1:
                    # Last turn: the final_response is the answer
                    turn_info["assistant_response"] = final_response
                react_trace.append(turn_info)

            # Build result
            result = {
                "example_id": example["id"],
                "problem": example["problem"],
                "model": llm_client.model,
                "final_response": final_response,
                "original_data": {
                    k: v
                    for k, v in example.items()
                    if not hasattr(v, "save") and not k.startswith("_")
                },
                "full_traces": {},
                "dataset_name": task_name,
                "retrieval_type": "local_api_react",
                "has_retrieval_content": any(r.has_content for r in retrieval_results),
                "usage": usage,
                "success": True,
                "react_turns": turns_used,
                "react_search_queries": all_search_queries,
                "react_trace": react_trace,
                "timing": {
                    "retrieval_time": total_retrieval_time,
                    "llm_time": total_llm_time,
                    "total_time": total_time,
                },
            }

            # Add retrieval info from first round
            if retrieval_results[0].source_url:
                result["used_url"] = retrieval_results[0].source_url
            if retrieval_results[0].images:
                result["retrieved_images"] = [
                    {"path": path, "score": score}
                    for path, score in retrieval_results[0].images
                ]
            # All retrieved images across all rounds
            all_images = []
            for rr in retrieval_results:
                for path, score in rr.images:
                    all_images.append({"path": path, "score": score})
            if len(retrieval_results) > 1:
                result["all_retrieved_images"] = all_images

            # Incremental save
            if output_file:
                with open(output_file, "a") as f:
                    f.write(json.dumps(result) + "\n")

            return result

        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            example_id = example.get("id", "unknown")

            if progress_counter is not None:
                progress_counter["completed"] += 1
                logger.warning(f"ReAct example {example_id} failed: {e}")

            logger.error(f"Error processing (react) {example_id}: {e}")
            logger.error(f"Traceback: {error_trace}")
            result = {
                "example_id": example.get("id"),
                "problem": example.get("problem"),
                "model": llm_client.model,
                "final_response": None,
                "original_data": {
                    k: v
                    for k, v in example.items()
                    if not hasattr(v, "save") and not k.startswith("_")
                },
                "dataset_name": task_name,
                "retrieval_type": "local_api_react",
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "timing": {
                    "retrieval_time": None,
                    "llm_time": None,
                    "total_time": None,
                },
            }
            if output_file:
                with open(output_file, "a") as f:
                    f.write(json.dumps(result) + "\n")
            return result
