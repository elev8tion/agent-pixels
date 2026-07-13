class Source:
    def __iter__(self) -> Iterator[Document]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
