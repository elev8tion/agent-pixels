def __iter__(self) -> Iterator[Document]:
        for i, url in enumerate(self._urls):
            yield Document(
                id=f"web_{i:06d}",
                url=url,
                metadata={"type": "web", "source_url": url},
            )
