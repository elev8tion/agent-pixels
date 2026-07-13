class BaseRetriever(ABC):
    """Base class for retrieval strategies."""

    @abstractmethod
    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        """Retrieve relevant content for the query.

        Args:
            query: The question/query text.
            example: The full example dict (may contain metadata, prepared data, etc.).

        Returns:
            RetrievalResult with retrieved content.
        """
        raise NotImplementedError
