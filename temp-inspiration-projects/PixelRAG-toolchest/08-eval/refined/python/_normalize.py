@staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for fuzzy DOM matching."""
        import re
        import unicodedata

        text = re.sub(r"[\xa0    ]", " ", text)
        text = re.sub(r"[‐-―−﹘﹣－—–]", "-", text)
        text = re.sub(r" +", " ", text)
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        return text.lower()
