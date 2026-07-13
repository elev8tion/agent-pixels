def _path_to_url(self, path: str, base_url: str) -> str:
        """Convert ZIM entry path to kiwix-serve URL with given base."""
        safe_chars = "/:@!$&'()*+,;="
        return f"{base_url}/content/{self.book_name}/{quote(path, safe=safe_chars)}"
