async def prefetch(self, examples: list[dict]):
        await self._text_retriever.prefetch(examples)
