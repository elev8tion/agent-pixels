def _get_wiki_lang(self, url: str) -> str:
        """Extract Wikipedia language code from URL."""
        import re

        match = re.match(r"https?://([a-z]{2,3})\.wikipedia\.org", url)
        return match.group(1) if match else "en"
