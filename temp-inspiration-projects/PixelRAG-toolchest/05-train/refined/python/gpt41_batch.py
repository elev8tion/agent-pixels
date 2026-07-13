async def gpt41_batch(client, queries, batch_idx, semaphore):
    async with semaphore:
        block = "\n".join(f"[{i}] {q}" for i, q in enumerate(queries))
        for attempt in range(3):
            try:
                resp = await client.post(
                    "/chat/completions",
                    json={
                        "model": "gpt-4.1-mini",
                        "messages": [
                            {"role": "system", "content": GPT41_SYSTEM},
                            {
                                "role": "user",
                                "content": GPT41_USER.format(
                                    n=len(queries), block=block
                                ),
                            },
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
                if isinstance(labels, list):
                    while len(labels) < len(queries):
                        labels.append(0)
                    return batch_idx, [int(bool(x)) for x in labels[: len(queries)]]
                return batch_idx, [0] * len(queries)
            except Exception as e:
                if attempt == 2:
                    logger.warning(f"Batch {batch_idx}: {e}")
                    return batch_idx, [0] * len(queries)
                await asyncio.sleep(2**attempt)
