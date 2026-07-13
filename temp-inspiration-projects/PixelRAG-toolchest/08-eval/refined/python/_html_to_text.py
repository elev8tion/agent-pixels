def _html_to_text(self, html: str) -> str:
        """Convert Wikipedia HTML to plain text, preserving table content."""
        import re
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted elements
        for tag in soup.find_all(["script", "style", "link", "meta"]):
            tag.decompose()

        # Remove edit section links
        for tag in soup.find_all("span", class_="mw-editsection"):
            tag.decompose()

        # Remove reference numbers [1], [2], etc.
        for tag in soup.find_all("sup", class_="reference"):
            tag.decompose()

        # Get text
        text = soup.get_text(separator="\n", strip=True)

        # Clean up excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text
