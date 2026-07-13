def _extract_wiki_title(self, url: str) -> str | None:
        """Extract Wikipedia page title from URL."""
        import re
        from urllib.parse import unquote

        # Match patterns like:
        # https://en.wikipedia.org/wiki/Python_(programming_language)
        # https://zh.wikipedia.org/wiki/Artificial_intelligence
        pattern = r"https?://[a-z]{2,3}\.wikipedia\.org/wiki/(.+?)(?:#.*)?$"
        match = re.match(pattern, url)
        if match:
            title = unquote(match.group(1))
            # Replace underscores with spaces
            title = title.replace("_", " ")
            return title
        return None
