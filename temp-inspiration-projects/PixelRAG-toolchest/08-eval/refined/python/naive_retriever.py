class NaiveRetriever(BaseRetriever):
    """No retrieval - returns empty result, LLM answers from its own knowledge."""

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        return RetrievalResult(retrieval_type="naive")
