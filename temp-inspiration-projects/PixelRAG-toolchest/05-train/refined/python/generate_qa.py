async def generate_qa(
    client: genai.Client,
    openai_client: openai.AsyncOpenAI | None,
    semaphore: asyncio.Semaphore,
    token_counter: dict,
    model: str,
    openai_fallback_model: str,
    fewshot_block: str,
    work_item: dict,
) -> dict | None:
    prompt = build_prompt(
        fewshot_block, work_item["passage"], work_item["focus_paragraph"]
    )

    async with semaphore:
        for attempt in range(5):
            try:
                text = await call_gemini(client, model, prompt, token_counter)

                qa = parse_model_output(text)
                if not qa:
                    return None
                if not is_natural_question(qa, work_item["passage"]):
                    return None
                return {
                    **qa,
                    "article_id": work_item["article_id"],
                    "article_n_chunks": work_item["article_n_chunks"],
                    "article_text_length": work_item["article_text_length"],
                    "chunk_index": work_item["chunk_index"],
                    "char_offset": work_item["char_offset"],
                    "n_tokens": work_item["n_tokens"],
                    "title_guess": work_item["title_guess"],
                    "focus_paragraph": work_item["focus_paragraph"],
                    "passage": work_item["passage"],
                    "generator_model": model,
                }
            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    if openai_client is not None:
                        try:
                            print(
                                f"  Gemini rate limited for article {work_item['article_id']}; "
                                f"falling back to {openai_fallback_model}"
                            )
                            text = await call_openai_fallback(
                                openai_client,
                                openai_fallback_model,
                                prompt,
                                token_counter,
                            )
                            qa = parse_model_output(text)
                            if not qa:
                                return None
                            if not is_natural_question(qa, work_item["passage"]):
                                return None
                            return {
                                **qa,
                                "article_id": work_item["article_id"],
                                "article_n_chunks": work_item["article_n_chunks"],
                                "article_text_length": work_item["article_text_length"],
                                "chunk_index": work_item["chunk_index"],
                                "char_offset": work_item["char_offset"],
                                "n_tokens": work_item["n_tokens"],
                                "title_guess": work_item["title_guess"],
                                "focus_paragraph": work_item["focus_paragraph"],
                                "passage": work_item["passage"],
                                "generator_model": openai_fallback_model,
                            }
                        except Exception as openai_error:
                            print(
                                f"  OpenAI fallback failed for article {work_item['article_id']}: "
                                f"{openai_error}"
                            )
                    wait = 2**attempt * 10 + random.uniform(1, 3)
                    print(f"  Rate limited, waiting {wait:.0f}s...")
                    await asyncio.sleep(wait)
                elif attempt < 4:
                    await asyncio.sleep(2)
                else:
                    print(
                        f"  Failed after 5 attempts for article {work_item['article_id']}: {e}"
                    )
                    return None
    return None
