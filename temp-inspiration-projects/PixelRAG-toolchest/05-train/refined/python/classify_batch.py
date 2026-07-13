async def classify_batch(client, queries, batch_idx, semaphore, model="gpt-4.1-mini"):
    """Classify a batch, returns list of 0/1."""
    async with semaphore:
        queries_block = "\n".join(f"[{i}] {q}" for i, q in enumerate(queries))
        user_msg = USER_TEMPLATE.format(n=len(queries), queries_block=queries_block)

        for attempt in range(3):
            try:
                resp = await client.post(
                    "/chat/completions",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": STRICT_SYSTEM},
                            {"role": "user", "content": user_msg},
                        ],
                        "temperature": 0,
                        "max_tokens": 300,
                    },
                    timeout=60,
                )
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"].strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                labels = json.loads(content)
                if isinstance(labels, list) and len(labels) == len(queries):
                    return batch_idx, [int(bool(x)) for x in labels]
                # Fallback: if wrong length, try to pad/truncate
                if isinstance(labels, list):
                    labels = labels[: len(queries)]
                    while len(labels) < len(queries):
                        labels.append(0)
                    return batch_idx, [int(bool(x)) for x in labels]
                return batch_idx, [0] * len(queries)
            except Exception as e:
                if attempt == 2:
                    logger.warning(f"Batch {batch_idx} failed: {e}")
                    return batch_idx, [0] * len(queries)
                await asyncio.sleep(2**attempt)
