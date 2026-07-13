def build_messages(
    query: str,
    retrieval_result: RetrievalResult,
    encode_image_fn=None,
    additional_instructions: str | None = None,
    few_shot_demos: list[dict] | None = None,
) -> list[dict]:
    """Build messages for LLM based on retrieval result.

    When ``retrieval_result.pixel_query_path`` is set the query is sent as an
    image. Two modes:
    - **Multimodal** (retrieval_type contains "multimodal"): text question + query image + retrieved tiles.
    - **Pixel query** (rendered question as image): first image = question, then retrieved tiles.
    """
    # ---- Multimodal / pixel-query mode: text + raw species/landmark photo + retrieved tiles ----
    # query_image_path = raw species/landmark photo (for generation, always).
    # pixel_query_path = rendered card or raw photo (for retrieval only; ignored here).
    # Falls back to pixel_query_path if query_image_path is not set (backward compat).
    gen_image_path = (
        retrieval_result.query_image_path or retrieval_result.pixel_query_path
    )
    if gen_image_path and encode_image_fn:
        system_prompt = SYSTEM_PROMPT_MULTIMODAL_QUERY
        # Decide evidence_note based on what retrieval actually returned. Three cases:
        #   (a) retrieved images (screenshot retrieval) — evidence is image tiles after the query
        #   (b) retrieved text (text retrieval) — evidence is rendered as text after the query
        #   (c) no retrieval — query image only
        # Until 2026-04-29 this branch silently dropped retrieval_result.text whenever the
        # query image was set, turning every "EVQA + text retrieval" cell into an effective
        # naive run. Fixed by adding the text-passages block alongside the multimodal preamble.
        if retrieval_result.images:
            evidence_note = "The first image is the query image. The following images are retrieved Wikipedia evidence. Answer the question based on the evidence."
        elif retrieval_result.text:
            evidence_note = "The image is the query image. Below is retrieved Wikipedia evidence (text). Answer the question based on the evidence and the image."
        else:
            evidence_note = "The first image is the query image. Answer the question based on the image (no additional evidence was retrieved)."
        text_parts = [
            f"Question: {query}",
            "",
            evidence_note,
        ]
        if retrieval_result.text:
            # Option 1: no URL header in multimodal branch either. Reader gets the
            # chunks and the query image, no metadata leak.
            text_parts.extend(
                [
                    "",
                    retrieval_result.text,
                ]
            )
        if additional_instructions:
            text_parts.append("")
            text_parts.append(additional_instructions)
        user_content: list[dict] = [
            {"type": "text", "text": "\n".join(text_parts)},
        ]

        # Add raw species/landmark photo
        if os.path.exists(gen_image_path):
            try:
                img_base64 = encode_image_fn(gen_image_path)
                if img_base64:
                    user_content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_base64}"},
                        }
                    )
            except Exception as e:
                logger.warning(f"Failed to encode query image {gen_image_path}: {e}")
                user_content.append(
                    {"type": "text", "text": f"(Image unavailable) Query: {query}"}
                )
        else:
            logger.warning(f"Query image not found: {gen_image_path}")
            user_content.append({"type": "text", "text": f"Query: {query}"})

        # Add retrieved tiles
        if retrieval_result.images:
            for img_path, score in retrieval_result.images:
                if os.path.exists(img_path):
                    try:
                        img_base64 = encode_image_fn(img_path)
                        if img_base64:
                            user_content.append(
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{img_base64}"
                                    },
                                }
                            )
                    except Exception as e:
                        logger.warning(f"Failed to encode image {img_path}: {e}")

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

    # ---- Original modes --------------------------------------------------
    # Select system prompt based on retrieval type
    if retrieval_result.base64_image:
        system_prompt = SYSTEM_PROMPT_SCREENSHOT
        user_content = [
            {"type": "text", "text": query},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{retrieval_result.base64_image}"
                },
            },
        ]
    elif (
        retrieval_result.retrieval_type == "text_api+rendered"
        and retrieval_result.images
        and encode_image_fn
    ):
        # Text retrieval rendered as images. Mirror the text-RAG framing so
        # evidence comes first and the reader sees an explicit "Question:"
        # suffix — same structure as the text→text branch below, only the
        # evidence modality differs.
        system_prompt = SYSTEM_PROMPT_TEXT_RAG
        user_content = []
        for img_path, score in retrieval_result.images:
            if os.path.exists(img_path):
                try:
                    img_base64 = encode_image_fn(img_path)
                    if img_base64:
                        user_content.append(
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                },
                            }
                        )
                except Exception as e:
                    logger.warning(f"Failed to encode image {img_path}: {e}")
        user_content.append({"type": "text", "text": f"Question: {query}"})
    elif retrieval_result.images and encode_image_fn:
        system_prompt = SYSTEM_PROMPT_VECTOR
        user_content = [{"type": "text", "text": query}]
        # Encode and add retrieved images
        for img_path, score in retrieval_result.images:
            if os.path.exists(img_path):
                try:
                    img_base64 = encode_image_fn(img_path)
                    if img_base64:
                        user_content.append(
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                },
                            }
                        )
                except Exception as e:
                    logger.warning(f"Failed to encode image {img_path}: {e}")
    elif retrieval_result.text:
        system_prompt = SYSTEM_PROMPT_TEXT_RAG
        # Option 1 (2026-04-29): no `Context from {urls}:` wrapper. URL leak gave
        # text retrieval an unfair advantage on entity-answering tasks. Reader sees
        # only the retrieved chunks and the question. URL still recorded in the
        # JSONL via retrieval_result.source_url for logging/grading.
        user_content = f"""{retrieval_result.text}

Question: {query}"""
    else:
        # Naive mode
        system_prompt = SYSTEM_PROMPT_NAIVE
        user_content = query

    # Append additional instructions (e.g. short-answer prompt for EM-eval tasks)
    if additional_instructions:
        if isinstance(user_content, str):
            user_content = user_content + "\n\n" + additional_instructions
        else:
            # list of content blocks — append as text
            user_content.append({"type": "text", "text": additional_instructions})

    # Few-shot as prior user/assistant turns (canonical chat few-shot format)
    if few_shot_demos and encode_image_fn:
        fewshot_turns = _build_fewshot_turns(few_shot_demos, encode_image_fn)
    else:
        fewshot_turns = []

    return [
        {"role": "system", "content": system_prompt},
        *fewshot_turns,
        {"role": "user", "content": user_content},
    ]
