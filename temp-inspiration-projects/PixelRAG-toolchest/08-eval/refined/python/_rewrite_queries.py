async def _rewrite_queries(self, examples: list[dict]) -> dict[str, str]:
        """Batch-rewrite questions into search queries using an LLM."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=self.rewrite_api_key,
            base_url=self.rewrite_api_base,
            timeout=60.0,
        )

        rewritten = {}
        sem = asyncio.Semaphore(20)

        async def rewrite_one(ex):
            eid = ex.get("id", "unknown")
            prompt = self.REWRITE_PROMPT.format(question=ex["problem"])
            async with sem:
                try:
                    resp = await client.chat.completions.create(
                        model=self.rewrite_model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
                        max_tokens=200,
                    )
                    rewritten[eid] = resp.choices[0].message.content.strip()
                except Exception as e:
                    logger.warning(f"Query rewrite failed for {eid}: {e}")
                    rewritten[eid] = ex["problem"]  # fallback to original

        await asyncio.gather(*[rewrite_one(ex) for ex in examples])
        return rewritten
