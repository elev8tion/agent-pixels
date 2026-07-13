@property
    def book_name(self) -> str:
        if self._book_name is None:
            self._book_name = self.zim_path.stem
        return self._book_name
